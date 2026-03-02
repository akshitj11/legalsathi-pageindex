"use client";

import { useState, useRef } from "react";
import { Mic, MicOff, Loader2 } from "lucide-react";

interface VoiceInputProps {
  onResult: (text: string) => void;
}

export default function VoiceInput({ onResult }: VoiceInputProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: "audio/webm;codecs=opus",
      });

      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data);
        }
      };

      mediaRecorder.onstop = async () => {
        setIsProcessing(true);
        const audioBlob = new Blob(chunksRef.current, { type: "audio/webm" });

        // Stop all tracks
        stream.getTracks().forEach((track) => track.stop());

        try {
          const backendUrl =
            process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

          const formData = new FormData();
          formData.append("audio", audioBlob, "recording.webm");

          const response = await fetch(`${backendUrl}/voice-to-text`, {
            method: "POST",
            body: formData,
          });

          if (response.ok) {
            const data = await response.json();
            if (data.text) {
              onResult(data.text);
            }
          }
        } catch (err) {
          console.error("Voice-to-text failed:", err);
        } finally {
          setIsProcessing(false);
        }
      };

      mediaRecorder.start(250);
      setIsRecording(true);
    } catch (err) {
      console.error("Microphone access denied:", err);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const handleClick = () => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  return (
    <button
      onClick={handleClick}
      disabled={isProcessing}
      className={`
        p-2 border-2 border-primary shadow-brutal-sm
        transition-all duration-100
        hover:translate-x-[1px] hover:translate-y-[1px] hover:shadow-none
        disabled:opacity-50 disabled:pointer-events-none
        ${isRecording ? "bg-red-500 text-white animate-pulse" : "bg-surface text-primary"}
      `}
      title={isRecording ? "Recording... Click to stop" : "Click to speak"}
    >
      {isProcessing ? (
        <Loader2 className="w-5 h-5 animate-spin" />
      ) : isRecording ? (
        <MicOff className="w-5 h-5" />
      ) : (
        <Mic className="w-5 h-5" />
      )}
    </button>
  );
}
