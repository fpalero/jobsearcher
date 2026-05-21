import { Component, Input, Output, EventEmitter } from '@angular/core';
import { Job } from '../../models/job.model';
import { JobService } from '../../services/job.service';

@Component({
  selector: 'app-job-detail-modal',
  standalone: true,
  imports: [],
  templateUrl: './job-detail-modal.component.html',
  styleUrl: './job-detail-modal.component.css'
})
export class JobDetailModalComponent {
  @Input({ required: true }) job!: Job;
  @Output() close = new EventEmitter<void>();
  logoError = false;
  generating = false;

  constructor(private jobService: JobService) {}

  onBackdropClick(event: MouseEvent) {
    if ((event.target as HTMLElement).id === 'modal-container') {
      this.close.emit();
    }
  }

  openApplyLink() {
    if (this.job.applyLink) {
      window.open(this.job.applyLink, '_blank', 'noopener,noreferrer');
    }
  }

  generateTailoredCV() {
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
        console.error('Failed to generate tailored CV:', err);
        this.generating = false;
      },
      complete: () => {
        this.generating = false;
      },
    });
  }

  generateCoverLetter() {
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
