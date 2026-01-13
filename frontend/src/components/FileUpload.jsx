import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import Papa from 'papaparse';

function FileUpload({ onFileUploaded }) {
    const onDrop = useCallback((acceptedFiles) => {
        const file = acceptedFiles[0];
        if (!file) return;

        // Parse CSV with PapaParse
        Papa.parse(file, {
            header: true,
            skipEmptyLines: true,
            complete: (results) => {
                console.log('Parsed CSV data:', results.data);
                onFileUploaded(results.data, file.name);
            },
            error: (error) => {
                console.error('Error parsing CSV:', error);
                alert('Failed to parse CSV file. Please check the format.');
            }
        });
    }, [onFileUploaded]);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: {
            'text/csv': ['.csv'],
            'application/vnd.ms-excel': ['.xls'],
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx']
        },
        multiple: false
    });

    return (
        <div
            {...getRootProps()}
            className={`
        border-2 border-dashed rounded-lg p-12 text-center cursor-pointer
        transition-all duration-300 ease-in-out
        ${isDragActive
                    ? 'border-blue-500 bg-blue-50 scale-105'
                    : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'
                }
      `}
        >
            <input {...getInputProps()} />
            <div className="space-y-4">
                <div className="text-6xl">📊</div>
                {isDragActive ? (
                    <p className="text-lg font-medium text-blue-600">Drop your file here...</p>
                ) : (
                    <>
                        <p className="text-lg font-medium text-gray-700">
                            Drag & drop your sales data file here
                        </p>
                        <p className="text-sm text-gray-500">
                            or click to select a file
                        </p>
                        <p className="text-xs text-gray-400 mt-2">
                            Supported formats: CSV, XLS, XLSX
                        </p>
                    </>
                )}
            </div>
        </div>
    );
}

export default FileUpload;
