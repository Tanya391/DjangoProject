import React, { useState } from 'react';
import { Upload, Database, CheckCircle2, AlertCircle, FileText, Sparkles, RefreshCw } from 'lucide-react';
import { api } from '../services/api';
import { useQueryClient } from '@tanstack/react-query';

export function DataManagementPage() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(null);
  const [uploadError, setUploadError] = useState(null);

  const [seeding, setSeeding] = useState(false);
  const [seedSuccess, setSeedSuccess] = useState(null);
  const [seedError, setSeedError] = useState(null);

  const queryClient = useQueryClient();

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
      setUploadSuccess(null);
      setUploadError(null);
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!selectedFile) return;

    setUploading(true);
    setUploadSuccess(null);
    setUploadError(null);

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const res = await api.uploadCSV(formData);
      if (res.inserted_count !== undefined) {
        if (res.inserted_count > 0) {
          setUploadSuccess(`Successfully imported ${res.inserted_count} transactions. (Ignored ${res.invalid_count} invalid, ${res.duplicate_count} duplicates)`);
        } else {
          setUploadError(`Failed to import any transactions. ${res.invalid_count} rows had formatting errors. Ensure columns match: date, receiver, description, amount, transaction_type, balance.`);
        }
      } else {
        setUploadSuccess(res.message || 'Transactions uploaded successfully!');
      }
      setSelectedFile(null);
      // Invalidate analytics queries to update dashboard
      queryClient.invalidateQueries();
    } catch (err) {
      setUploadError(err.message || 'Failed to upload CSV file.');
    } finally {
      setUploading(false);
    }
  };

  const handleSeed = async () => {
    setSeeding(true);
    setSeedSuccess(null);
    setSeedError(null);

    try {
      const res = await api.seedDemoData();
      setSeedSuccess(res.message || 'Demo data loaded successfully!');
      queryClient.invalidateQueries();
    } catch (err) {
      setSeedError(err.message || 'Failed to generate demo data.');
    } finally {
      setSeeding(false);
    }
  };

  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      {/* Page Title */}
      <div>
        <h2 className="text-2xl font-extrabold text-slate-900 dark:text-white tracking-tight">Data Management</h2>
        <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">
          Upload bank CSV statements or load sample transaction sets.
        </p>
      </div>

      {/* Grid of Two Distinct Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Card 1: CSV Upload */}
        <div className="glass-card p-6 rounded-2xl border border-slate-200 dark:border-slate-800 space-y-4 flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 mb-3">
              <div className="p-2 rounded-xl bg-indigo-50 dark:bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 border border-indigo-200 dark:border-indigo-500/20">
                <Upload className="w-5 h-5" />
              </div>
              <h3 className="text-base font-bold text-slate-900 dark:text-white">Upload Bank Statement (CSV)</h3>
            </div>
            <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed mb-4">
              Upload your bank CSV statement to ingest financial records.
            </p>

            {/* Drag & Drop Input Container */}
            <form onSubmit={handleUpload} className="space-y-4">
              <label className="flex flex-col items-center justify-center border-2 border-dashed border-slate-300 dark:border-slate-700 hover:border-indigo-500 rounded-2xl p-6 cursor-pointer bg-slate-50/70 dark:bg-slate-900/50 hover:bg-slate-100 dark:hover:bg-slate-900/80 transition group">
                <FileText className="w-8 h-8 text-slate-400 dark:text-slate-500 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 mb-2 transition-colors" />
                <span className="text-xs font-semibold text-slate-700 dark:text-slate-300">
                  {selectedFile ? selectedFile.name : 'Click or drop CSV statement here'}
                </span>
                <input type="file" accept=".csv" onChange={handleFileChange} className="hidden" />
              </label>

              {uploadSuccess && (
                <div className="p-3 rounded-xl bg-emerald-50 dark:bg-emerald-500/10 border border-emerald-200 dark:border-emerald-500/20 text-emerald-700 dark:text-emerald-400 text-xs flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 shrink-0" />
                  {uploadSuccess}
                </div>
              )}

              {uploadError && (
                <div className="p-3 rounded-xl bg-rose-50 dark:bg-rose-500/10 border border-rose-200 dark:border-rose-500/20 text-rose-700 dark:text-rose-400 text-xs flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 shrink-0" />
                  {uploadError}
                </div>
              )}

              <button
                type="submit"
                disabled={!selectedFile || uploading}
                className="w-full py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 text-white font-semibold text-xs rounded-xl shadow-lg transition flex items-center justify-center gap-2"
              >
                {uploading ? 'Processing & Indexing CSV...' : 'Process Statement File'}
              </button>
            </form>
          </div>
        </div>

        {/* Card 2: Seed Demo Data */}
        <div className="glass-card p-6 rounded-2xl border border-slate-200 dark:border-slate-800 space-y-4 flex flex-col justify-between bg-gradient-to-br from-white via-slate-50 to-indigo-50/40 dark:from-slate-900 dark:via-slate-900 dark:to-indigo-950/30">
          <div>
            <div className="flex items-center gap-2 mb-3">
              <div className="p-2 rounded-xl bg-cyan-50 dark:bg-cyan-500/10 text-cyan-600 dark:text-cyan-400 border border-cyan-200 dark:border-cyan-500/20">
                <Database className="w-5 h-5" />
              </div>
              <h3 className="text-base font-bold text-slate-900 dark:text-white">Generate Sample Data</h3>
            </div>
            <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed mb-6">
              Populate the application with sample multi-month transaction records.
            </p>

            <div className="p-4 rounded-xl bg-slate-100/80 dark:bg-slate-950/60 border border-slate-200 dark:border-slate-800 space-y-2 mb-6">
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-600 dark:text-slate-400">Sample Records:</span>
                <span className="text-slate-900 dark:text-slate-200 font-bold">80+ Transactions</span>
              </div>
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-600 dark:text-slate-400">Merchant Types:</span>
                <span className="text-indigo-600 dark:text-indigo-400 font-bold">Swiggy, Netflix, Amazon, Uber</span>
              </div>
            </div>

            {seedSuccess && (
              <div className="p-3 mb-4 rounded-xl bg-emerald-50 dark:bg-emerald-500/10 border border-emerald-200 dark:border-emerald-500/20 text-emerald-700 dark:text-emerald-400 text-xs flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 shrink-0" />
                {seedSuccess}
              </div>
            )}

            {seedError && (
              <div className="p-3 mb-4 rounded-xl bg-rose-50 dark:bg-rose-500/10 border border-rose-200 dark:border-rose-500/20 text-rose-700 dark:text-rose-400 text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0" />
                {seedError}
              </div>
            )}
          </div>

          <button
            onClick={handleSeed}
            disabled={seeding}
            className="w-full py-2.5 bg-gradient-to-r from-cyan-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 disabled:opacity-50 text-white font-semibold text-xs rounded-xl shadow-lg transition flex items-center justify-center gap-2"
          >
            {seeding ? (
              'Seeding Demo Transactions...'
            ) : (
              <>
                <Sparkles className="w-4 h-4 text-cyan-200" />
                Load Sample Transactions
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
