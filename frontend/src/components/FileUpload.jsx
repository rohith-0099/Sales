import { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';

function FileUpload({ onFileSelected, disabled = false }) {
  const onDrop = useCallback(
    (acceptedFiles) => {
      const file = acceptedFiles[0];
      if (!file || disabled) {
        return;
      }

      onFileSelected(file);
    },
    [disabled, onFileSelected],
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
    },
    multiple: false,
    disabled,
  });

  return (
    <div
      {...getRootProps()}
      className={[
        'rounded-3xl border-2 border-dashed px-8 py-12 text-center transition',
        disabled
          ? 'cursor-not-allowed border-slate-200 bg-slate-100 text-slate-400'
          : isDragActive
            ? 'cursor-pointer border-emerald-500 bg-emerald-50 text-emerald-700'
            : 'cursor-pointer border-slate-300 bg-slate-50 text-slate-700 hover:border-emerald-400 hover:bg-white',
      ].join(' ')}
    >
      <input {...getInputProps()} />
      <div className="space-y-3">
        <p className="text-sm font-semibold uppercase tracking-[0.2em] text-slate-500">
          Sales Data Upload
        </p>
        <h3 className="text-2xl font-semibold text-slate-900">
          {isDragActive ? 'Drop the file to upload it' : 'Drag a CSV or XLSX file here'}
        </h3>
        <p className="mx-auto max-w-2xl text-sm text-slate-600">
          The backend will normalize dates, detect sales columns, infer dataset granularity, and prepare
          product-level indexing for search.
        </p>
        <p className="text-xs text-slate-500">Supported formats: .csv and .xlsx</p>
      </div>
    </div>
  );
}

export default FileUpload;
