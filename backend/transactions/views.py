"""
API Views — wired to query parser, query router, hybrid retrieval, and analytics engine.
"""

from django.contrib.auth.models import User
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from .llm_service import answer_question_with_context
from .query_parser import parse_query
from .query_router import route_query, execute_analytics_route, ROUTE_ANALYTICS, ROUTE_RETRIEVAL, ROUTE_RAG
from .retrieval import retrieve_transactions_for_query
from .serializers import (
    AskQuestionRequestSerializer,
    RegisterRequestSerializer,
    RetrieveRequestSerializer,
)
from .analytics_service import (
    get_monthly_summary,
    get_category_breakdown,
    get_top_merchants,
    get_cashflow,
    detect_subscriptions,
)
from .services import generate_demo_data, ingest_csv
import os
import tempfile
from rest_framework.parsers import MultiPartParser, FormParser

def _get_user_id(request) -> str | None:
    """Return a string user_id from the authenticated request, or None."""
    if request.user and request.user.is_authenticated:
        return str(request.user.id)
    return None


# ---------------------------------------------------------------------------
# Auth views
# ---------------------------------------------------------------------------

class RegisterView(generics.GenericAPIView):
    serializer_class = RegisterRequestSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            first_error = next(iter(serializer.errors.values()))
            message = first_error[0] if isinstance(first_error, list) and first_error else first_error
            return Response({"error": str(message)}, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        user = User.objects.create_user(
            username=data["username"],
            email=data.get("email", ""),
            password=data["password"],
        )
        return Response(
            {
                "message": "User registered successfully",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                },
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]


class LogoutView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return Response(
            {"message": "Logged out successfully. Remove access and refresh tokens on client."},
            status=status.HTTP_200_OK,
        )


class StatusView(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            "status": "ok",
        })


# ---------------------------------------------------------------------------
# Retrieval view
# ---------------------------------------------------------------------------

class RetrieveTransactionsView(generics.GenericAPIView):
    serializer_class = RetrieveRequestSerializer
    permission_classes = [IsAuthenticated]

    def _handle(self, data, request):
        serializer = self.get_serializer(data=data)
        if not serializer.is_valid():
            first_error = next(iter(serializer.errors.values()))
            message = first_error[0] if isinstance(first_error, list) and first_error else first_error
            return Response({"error": str(message)}, status=status.HTTP_400_BAD_REQUEST)

        question = serializer.validated_data["question"]
        top_k = serializer.validated_data["k"]
        user_id = _get_user_id(request)

        try:
            parsed = parse_query(question)
            results = retrieve_transactions_for_query(
                question=question,
                top_k=top_k,
                parsed=parsed,
                user_id=user_id,
            )
            return Response(
                {
                    "question": question,
                    "parsed_intent": parsed.intent,
                    "top_k": top_k,
                    "count": len(results),
                    "results": results,
                }
            )
        except Exception as exc:
            return Response({"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        return self._handle(request.data, request)

    def get(self, request):
        return self._handle(request.query_params, request)


# ---------------------------------------------------------------------------
# Ask view — query router + analytics + RAG
# ---------------------------------------------------------------------------

class AskQuestionView(generics.GenericAPIView):
    serializer_class = AskQuestionRequestSerializer
    permission_classes = [IsAuthenticated]

    def _handle(self, data, request):
        serializer = self.get_serializer(data=data)
        if not serializer.is_valid():
            first_error = next(iter(serializer.errors.values()))
            message = first_error[0] if isinstance(first_error, list) and first_error else first_error
            return Response({"error": str(message)}, status=status.HTTP_400_BAD_REQUEST)

        question = serializer.validated_data["question"]
        top_k = serializer.validated_data["k"]
        user_id = _get_user_id(request)

        try:
            parsed = parse_query(question)
            route = route_query(parsed)

            # --- Analytics route: deterministic, no LLM ---
            if route == ROUTE_ANALYTICS:
                analytics_result = execute_analytics_route(parsed, user_id)
                summary_answer = analytics_result.get("summary") or "Analytics computed successfully."
                response_data = {
                    "question": question,
                    "route": route,
                    "intent": parsed.intent,
                    "answer": summary_answer,
                    "data": analytics_result.get("data"),
                    "provider": "analytics_engine",
                    "provider_errors": [],
                    "sources": [],
                    "source_count": 0,
                    "confidence": 1.0,
                }
                from .models import QueryLog
                if user_id:
                    try:
                        u_obj = User.objects.filter(id=int(user_id)).first()
                        QueryLog.objects.create(
                            user=u_obj,
                            question=question,
                            route=route,
                            answer=summary_answer,
                            source_count=0
                        )
                    except Exception:
                        pass
                return Response(response_data)

            # --- Retrieval-only route ---
            if route == ROUTE_RETRIEVAL:
                transactions = retrieve_transactions_for_query(
                    question=question, top_k=top_k, parsed=parsed, user_id=user_id
                )
                return Response({
                    "question": question,
                    "route": route,
                    "intent": parsed.intent,
                    "answer": None,
                    "data": None,
                    "provider": "retrieval_engine",
                    "provider_errors": [],
                    "sources": transactions,
                    "source_count": len(transactions),
                    "confidence": None,
                })

            # --- RAG route: retrieval + LLM explanation ---
            transactions = retrieve_transactions_for_query(
                question=question, top_k=top_k, parsed=parsed, user_id=user_id
            )
            llm_result = answer_question_with_context(question=question, transactions=transactions)

            response_data = {
                "question": question,
                "route": route,
                "intent": parsed.intent,
                "answer": llm_result.get("answer"),
                "data": None,
                "provider": llm_result.get("provider"),
                "provider_errors": llm_result.get("provider_errors", []),
                "sources": transactions,
                "source_count": len(transactions),
                "confidence": _compute_confidence(transactions),
            }
            
            # Save to query history (Django ORM)
            from .models import QueryLog
            if user_id:
                try:
                    u_obj = User.objects.filter(id=int(user_id)).first()
                    QueryLog.objects.create(
                        user=u_obj,
                        question=question,
                        route=route,
                        answer=response_data.get("answer") or "",
                        source_count=response_data.get("source_count", 0),
                    )
                except Exception:
                    pass

            return Response(response_data)

        except Exception as exc:
            return Response({"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        return self._handle(request.data, request)

    def get(self, request):
        return self._handle(request.query_params, request)

class QueryHistoryView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = _get_user_id(request)
        if not user_id:
            return Response({"error": "Unauthorized"}, status=401)
        
        from .models import QueryLog
        from django.db.models import Q
        try:
            uid = int(user_id)
            logs = QueryLog.objects.filter(Q(user_id=uid) | Q(user__isnull=True)).order_by("-created_at")[:50]
            history = [l.to_dict() for l in logs]
            return Response({"history": history}, status=200)
        except Exception:
            return Response({"history": []}, status=200)
        except Exception as exc:
            return Response({"error": str(exc)}, status=500)


def _compute_confidence(transactions: list) -> float:
    """Simple confidence score based on source count and scores."""
    if not transactions:
        return 0.0
    scores = [t.get("final_score", 0.5) for t in transactions]
    avg = sum(scores) / len(scores)
    return round(min(avg, 1.0), 2)


# ---------------------------------------------------------------------------
# Analytics endpoints
# ---------------------------------------------------------------------------

class MonthlySummaryView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = _get_user_id(request)
        year = request.query_params.get("year")
        try:
            year = int(year) if year else None
            data = get_monthly_summary(user_id=user_id, year=year)
            return Response({"monthly_summary": data})
        except Exception as exc:
            return Response({"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CategoryBreakdownView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from datetime import date as date_type
        user_id = _get_user_id(request)
        try:
            data = get_category_breakdown(user_id=user_id)
            return Response({"category_breakdown": data})
        except Exception as exc:
            return Response({"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TopMerchantsView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = _get_user_id(request)
        limit = int(request.query_params.get("limit", 10))
        try:
            data = get_top_merchants(user_id=user_id, limit=limit)
            return Response({"top_merchants": data})
        except Exception as exc:
            return Response({"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CashflowView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = _get_user_id(request)
        try:
            data = get_cashflow(user_id=user_id)
            return Response({"cashflow": data})
        except Exception as exc:
            return Response({"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SubscriptionsView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = _get_user_id(request)
        try:
            data = detect_subscriptions(user_id=user_id)
            return Response({"subscriptions": data, "count": len(data)})
        except Exception as exc:
            return Response({"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SeedDemoDataView(generics.GenericAPIView):
    """
    POST /api/v1/seed/
    Generates 6 months of realistic dummy transaction data for the logged-in user.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_id = _get_user_id(request)
        if not user_id:
            return Response({"error": "User ID required"}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            # We can optionally read 'months' from request data if we want to allow flexibility
            months = int(request.data.get("months", 6))
            count = generate_demo_data(str(user_id), months=months)
            return Response({
                "message": f"Successfully generated {count} transactions.",
                "count": count
            }, status=status.HTTP_201_CREATED)
        except Exception as exc:
            return Response({"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UploadTransactionsView(generics.GenericAPIView):
    """
    POST /api/v1/upload/
    Uploads a CSV file of transactions and associates them with the logged-in user.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        user_id = _get_user_id(request)
        file_obj = request.FILES.get('file')

        if not file_obj:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        if not file_obj.name.endswith('.csv'):
            return Response({"error": "Only CSV files are supported"}, status=status.HTTP_400_BAD_REQUEST)

        # Save temporarily
        fd, temp_path = tempfile.mkstemp(suffix=".csv")
        try:
            with os.fdopen(fd, 'wb') as temp_file:
                for chunk in file_obj.chunks():
                    temp_file.write(chunk)
            
            # Ingest
            report = ingest_csv(temp_path, return_report=True, user_id=str(user_id))
            return Response(report, status=status.HTTP_200_OK)
        
        except Exception as exc:
            return Response({"error": f"Failed to process file: {str(exc)}"}, status=status.HTTP_400_BAD_REQUEST)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)



from django.db.models import Q
from .models import Transaction


class TransactionListView(generics.GenericAPIView):
    """
    GET /api/v1/transactions/
    Returns paginated list of transactions using Django ORM.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = _get_user_id(request)
        search = request.query_params.get("search", "").strip()
        category = request.query_params.get("category", "").strip()
        limit = int(request.query_params.get("limit", 100))
        offset = int(request.query_params.get("offset", 0))

        qs = Transaction.objects.all()
        if user_id:
            try:
                uid = int(user_id)
                qs = qs.filter(Q(user_id=uid) | Q(user__isnull=True))
            except (ValueError, TypeError):
                qs = qs.filter(user__isnull=True)

        if category:
            qs = qs.filter(category_name__iexact=category)

        if search:
            qs = qs.filter(
                Q(receiver__icontains=search)
                | Q(normalized_merchant__icontains=search)
                | Q(description__icontains=search)
            )

        total_count = qs.count()
        results = [t.to_dict() for t in qs.order_by("-date", "-created_at")[offset:offset + limit]]

        return Response({
            "count": total_count,
            "results": results
        })


