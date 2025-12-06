import { useState } from 'react';
import { motion } from 'framer-motion';
import { ArrowLeft, Upload, FileText, CheckCircle2, X } from 'lucide-react';

interface FileUploadProps {
  onComplete: () => void;
  onBack: () => void;
}

interface UploadedFile {
  id: string;
  name: string;
  size: number;
  type: string;
}

export function FileUpload({ onComplete, onBack }: FileUploadProps) {
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFiles(e.dataTransfer.files);
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFiles(e.target.files);
    }
  };

  const handleFiles = (fileList: FileList) => {
    const newFiles: UploadedFile[] = Array.from(fileList).map((file) => ({
      id: Math.random().toString(36).substr(2, 9),
      name: file.name,
      size: file.size,
      type: file.type,
    }));
    setFiles([...files, ...newFiles]);
  };

  const removeFile = (id: string) => {
    setFiles(files.filter((file) => file.id !== id));
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  return (
    <div className="min-h-screen bg-[#2820FF]">
      <div className="max-w-md mx-auto p-6 pb-32">
        <motion.button
          onClick={onBack}
          className="flex items-center gap-2 text-white/70 hover:text-white mb-6"
          style={{ fontFamily: 'Inter, sans-serif' }}
          whileHover={{ x: -4 }}
          whileTap={{ scale: 0.95 }}
        >
          <ArrowLeft className="w-5 h-5" />
          Back
        </motion.button>

        <motion.div
          className="mb-8"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <h1
            className="text-5xl text-white mb-3"
            style={{ fontFamily: '"Momo Trust Display", sans-serif', fontWeight: 800 }}
          >
            UPLOAD DOCS
          </h1>
          <p className="text-white/70" style={{ fontFamily: 'Inter, sans-serif' }}>
            Please upload your monthly settlement or payslip to verify your income
          </p>
        </motion.div>

        {/* Progress Bar */}
        <div className="flex gap-2 mb-8">
          <div className="flex-1 h-1 bg-[#FEFF09] rounded-full"></div>
          <div className="flex-1 h-1 bg-[#FEFF09] rounded-full"></div>
        </div>

        <motion.div
          className={`border-2 border-dashed rounded-[2.5rem] p-8 text-center transition-all ${
            dragActive
              ? 'border-[#FEFF09] bg-[#FEFF09]/10'
              : 'border-white/30 bg-white/5 backdrop-blur-md'
          }`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.1 }}
        >
          <div className="w-16 h-16 bg-[#FEFF09] rounded-full mx-auto flex items-center justify-center mb-4">
            <Upload className="w-8 h-8 text-[#0F172A]" />
          </div>
          <h3
            className="text-white mb-2"
            style={{ fontFamily: '"Momo Trust Display", sans-serif', fontWeight: 800 }}
          >
            Drop your files here
          </h3>
          <p className="text-white/60 text-sm mb-4" style={{ fontFamily: 'Inter, sans-serif' }}>
            or click to browse
          </p>
          <input
            type="file"
            multiple
            onChange={handleFileInput}
            className="hidden"
            id="file-upload"
            accept=".pdf,.jpg,.jpeg,.png"
          />
          <label
            htmlFor="file-upload"
            className="inline-block px-6 py-3 bg-[#FF44EC] text-white rounded-full cursor-pointer hover:bg-[#FF44EC]/90 transition-colors"
            style={{ fontFamily: '"Momo Trust Display", sans-serif', fontWeight: 800 }}
          >
            SELECT FILES
          </label>
          <p className="text-xs text-white/50 mt-4" style={{ fontFamily: 'Inter, sans-serif' }}>
            Supported formats: PDF, JPG, PNG (Max 10MB)
          </p>
        </motion.div>

        {files.length > 0 && (
          <motion.div
            className="mt-6 space-y-3"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
          >
            <h3
              className="text-sm text-white/70"
              style={{ fontFamily: 'Inter, sans-serif', fontWeight: 600 }}
            >
              Uploaded Files
            </h3>
            {files.map((file, index) => (
              <motion.div
                key={file.id}
                className="flex items-center gap-3 p-4 bg-[#FEFF09]/10 backdrop-blur-md border border-[#FEFF09]/30 rounded-3xl"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <CheckCircle2 className="w-5 h-5 text-[#FEFF09] flex-shrink-0" />
                <FileText className="w-5 h-5 text-white flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-white truncate" style={{ fontFamily: 'Inter, sans-serif', fontWeight: 600 }}>
                    {file.name}
                  </p>
                  <p className="text-xs text-white/50" style={{ fontFamily: 'Inter, sans-serif' }}>
                    {formatFileSize(file.size)}
                  </p>
                </div>
                <motion.button
                  onClick={() => removeFile(file.id)}
                  className="p-1 hover:bg-white/10 rounded-full"
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                >
                  <X className="w-4 h-4 text-white" />
                </motion.button>
              </motion.div>
            ))}
          </motion.div>
        )}

        <motion.button
          onClick={onComplete}
          disabled={files.length === 0}
          className="fixed bottom-6 left-6 right-6 max-w-md mx-auto bg-[#FEFF09] text-[#0F172A] py-5 rounded-full transition-all disabled:bg-white/20 disabled:text-white/40 disabled:cursor-not-allowed"
          style={{ fontFamily: '"Momo Trust Display", sans-serif', fontWeight: 800 }}
          whileHover={files.length > 0 ? { scale: 1.02 } : {}}
          whileTap={files.length > 0 ? { scale: 0.98 } : {}}
        >
          COMPLETE SETUP
        </motion.button>
      </div>
    </div>
  );
}