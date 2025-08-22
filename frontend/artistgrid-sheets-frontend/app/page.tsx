"use client";

import { Button } from "@/components/ui/button";
import { Github, FileDown, FileText, FileSpreadsheet } from "lucide-react";

const buttonData = [
  {
    name: "View on GitHub",
    href: "https://github.com/ArtistGrid/Sheets",
    icon: Github,
    isExternal: true,
  },
  {
    name: "Download CSV",
    href: "https://sheets.artistgrid.cx/artists.csv",
    icon: FileDown,
    downloadName: "artists.csv",
  },
  {
    name: "View HTML",
    href: "https://sheets.artistgrid.cx/artists.html",
    icon: FileText,
    isExternal: true,
  },
  {
    name: "Download XLSX",
    href: "https://sheets.artistgrid.cx/artists.xlsx",
    icon: FileSpreadsheet,
    downloadName: "ArtistGrid.xlsx",
  },
];

export default function ArtistGridSheets() {
  return (
    <div className="min-h-screen bg-black text-white flex items-center justify-center p-4 sm:p-6">
      <div className="w-full max-w-lg text-center bg-neutral-950 border border-neutral-800 rounded-2xl p-8 sm:p-12 shadow-2xl shadow-black/30 animate-in fade-in-0 zoom-in-95 duration-500">
        <h1 className="text-3xl sm:text-4xl font-bold bg-gradient-to-b from-neutral-50 to-neutral-400 bg-clip-text text-transparent mb-4">
          ArtistGrid Sheets
        </h1>
        <p className="text-neutral-400 mb-10 max-w-sm mx-auto">
          We pull from TrackerHub and parse it into a CSV file. Still a work in
          progress.
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {buttonData.map((button) => (
            <Button
              key={button.name}
              asChild
              className="bg-white text-black hover:bg-neutral-200 font-semibold rounded-lg h-14 text-base transition-all duration-300 ease-out hover:-translate-y-1 hover:shadow-[0_0_30px_rgba(255,255,255,0.3)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-offset-black focus-visible:ring-white"
            >
              <a
                href={button.href}
                {...(button.isExternal && {
                  target: "_blank",
                  rel: "noopener noreferrer",
                })}
                {...(button.downloadName && { download: button.downloadName })}
              >
                <button.icon className="w-5 h-5 mr-2.5" aria-hidden="true" />
                {button.name}
              </a>
            </Button>
          ))}
        </div>
      </div>
    </div>
  );
}