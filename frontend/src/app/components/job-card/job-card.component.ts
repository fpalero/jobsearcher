import { Component, Input, Output, EventEmitter } from '@angular/core';
import { Job } from '../../models/job.model';
import { JobService } from '../../services/job.service';

@Component({
  selector: 'app-job-card',
  standalone: true,
  imports: [],
  templateUrl: './job-card.component.html',
  styleUrl: './job-card.component.css'
})
export class JobCardComponent {
  @Input({ required: true }) job!: Job;
  @Output() viewDetails = new EventEmitter<Job>();
  isHovered = false;
  logoError = false;
  generating = false;

  constructor(private jobService: JobService) {}

  get matchOffset(): number {
    const circumference = 175.9;
    return circumference - (this.job.matchPercentage / 100) * circumference;
  }

  openApplyLink(event: Event) {
    event.stopPropagation();
    if (this.job.applyLink) {
      window.open(this.job.applyLink, '_blank', 'noopener,noreferrer');
    }
  }

  generateCV(event: Event) {
    event.stopPropagation();
    if (this.generating) return;
    this.generating = true;
    this.jobService.generateTailoredPdf(this.job.jobId).subscribe({
      next: (blob) => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `cv_${this.job.company.replace(/\s+/g, '_').toLowerCase()}.pdf`;
        a.click();
        window.URL.revokeObjectURL(url);
      },
      error: (err) => {
        console.error('Failed to generate CV:', err);
        this.generating = false;
      },
      complete: () => {
        this.generating = false;
      },
    });
  }

  generateCoverLetter(event: Event) {
    event.stopPropagation();
    if (this.generating) return;
    this.generating = true;
    this.jobService.generateCoverLetterPdf(this.job.jobId).subscribe({
      next: (blob) => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `cover_letter_${this.job.company.replace(/\s+/g, '_').toLowerCase()}.pdf`;
        a.click();
        window.URL.revokeObjectURL(url);
      },
      error: (err) => {
        console.error('Failed to generate cover letter:', err);
        this.generating = false;
      },
      complete: () => {
        this.generating = false;
      },
    });
  }
}
