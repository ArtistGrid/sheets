'use client';

import { Button } from "@/components/ui/button";
import { Download, Github } from "lucide-react";
import { Fade } from "react-awesome-reveal";

export default function Component() {
  return (
    <div className="min-h-screen bg-background text-foreground flex items-center justify-center p-4">
      <div className="max-w-2xl mx-auto text-center space-y-8">
        <Fade triggerOnce>
          <h1 className="text-4xl md:text-6xl font-bold tracking-tight">
            ArtistGrid Sheets
          </h1>
        </Fade>

        <Fade delay={200} triggerOnce>
          <p className="text-lg md:text-xl text-muted-foreground leading-relaxed">
            We pull from{" "}
            <a
              href="https://docs.google.com/spreadsheets/d/1zoOIaNbBvfuL3sS3824acpqGxOdSZSIHM8-nI9C-Vfc/htmlview"
              className="underline text-white"
              target="_blank"
              rel="noopener noreferrer"
            >
              TrackerHub
            </a>{" "}
            and parse it into a CSV file. Still a work in progress.
          </p>
        </Fade>

        <Fade delay={400} triggerOnce>
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <a
              href="https://github.com/ArtistGrid/Sheets"
              target="_blank"
              rel="noopener noreferrer"
            >
              <Button size="lg" className="w-full sm:w-auto">
                <Github className="mr-2 h-5 w-5" />
                View on GitHub
              </Button>
            </a>

            <Button
              variant="outline"
              size="lg"
              className="w-full sm:w-auto bg-transparent"
            >
              <Download className="mr-2 h-5 w-5" />
              <a
              href="https://sheets.artistgrid.cx/artists.csv"
              target="_blank"
              rel="noopener noreferrer"
            > Download CSV</a>
            </Button>
          </div>
        </Fade>
      </div>
    </div>
  );
}
