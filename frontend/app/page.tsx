"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import UploadZone from "@/components/UploadZone";
import { uploadPDF } from "@/lib/api";
import { FileText, Shield, Mic, Languages } from "lucide-react";

export default function Home() {
  const router = useRouter();
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleUpload = async (file: File) => {
    setIsUploading(true);
    setError(null);

    try {
      const { doc_id } = await uploadPDF(file);
      router.push(`/analyze/${doc_id}`);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Upload failed. Try again."
      );
      setIsUploading(false);
    }
  };

  return (
    <main className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b-4 border-primary bg-surface">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="bg-primary text-background p-2 border-2 border-primary shadow-brutal-sm">
              <FileText className="w-6 h-6" />
            </div>
            <h1 className="text-2xl font-bold tracking-tight">LegalSaathi</h1>
          </div>
          <span className="text-text-secondary text-sm font-medium">
            AI Legal Document Analyzer
          </span>
        </div>
      </header>

      {/* Hero Section */}
      <section className="max-w-4xl mx-auto px-6 pt-16 pb-8">
        <div className="text-center mb-12">
          <h2 className="text-5xl font-bold leading-tight mb-4">
            Apne Legal Documents
            <br />
            <span className="inline-block bg-primary text-background px-4 py-1 mt-2 shadow-brutal">
              Samjho Simply
            </span>
          </h2>
          <p className="text-text-secondary text-lg mt-6 max-w-2xl mx-auto">
            Koi bhi legal document upload karo — rent agreement, job contract,
            loan paper — hum aapko simple Hindi mein samjha denge.
          </p>
        </div>

        {/* Upload Zone */}
        <div className="max-w-xl mx-auto">
          <UploadZone onUpload={handleUpload} isUploading={isUploading} />

          {error && (
            <div className="mt-4 bg-red-50 border-2 border-red-500 p-3 shadow-brutal-sm">
              <p className="text-red-700 font-medium text-sm">{error}</p>
            </div>
          )}
        </div>
      </section>

      {/* Features */}
      <section className="max-w-4xl mx-auto px-6 py-16">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <FeatureCard
            icon={<Shield className="w-6 h-6" />}
            title="Simple Explanation"
            description="Legal jargon ko simple Hindi mein convert karta hai. Koi bhi samajh sake."
          />
          <FeatureCard
            icon={<Mic className="w-6 h-6" />}
            title="Voice Support"
            description="Bol ke pucho, sun ke samjho. Hindi aur English dono mein."
          />
          <FeatureCard
            icon={<Languages className="w-6 h-6" />}
            title="Hindi + English"
            description="Document chahe English mein ho, jawab milega aapki bhasha mein."
          />
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t-4 border-primary bg-surface">
        <div className="max-w-6xl mx-auto px-6 py-6 text-center">
          <p className="text-text-secondary text-sm">
            LegalSaathi — Made for common Indians, powered by AI
          </p>
        </div>
      </footer>
    </main>
  );
}

function FeatureCard({
  icon,
  title,
  description,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
}) {
  return (
    <div className="card-brutal hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-brutal-hover transition-all duration-100">
      <div className="bg-primary text-background p-2 w-fit border-2 border-primary shadow-brutal-sm mb-3">
        {icon}
      </div>
      <h3 className="font-bold text-lg mb-2">{title}</h3>
      <p className="text-text-secondary text-sm">{description}</p>
    </div>
  );
}
