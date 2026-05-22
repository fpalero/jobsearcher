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
  generatingCV = false;
  generatingCoverLetter = false;

  constructor(private jobService: JobService) {}

  get isSaved(): boolean {
    return !!this.job?.saved;
  }

  get isApplied(): boolean {
    return !!this.job?.applied;
  }

  get isPositiveFeedback(): boolean {
    return this.job?.feedback === 'positive';
  }

  get isNegativeFeedback(): boolean {
    return this.job?.feedback === 'negative';
  }

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
    if (this.generatingCV) return;
    this.generatingCV = true;
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
        this.generatingCV = false;
      },
      complete: () => {
        this.generatingCV = false;
      },
    });
  }

  generateCoverLetter() {
    if (this.generatingCoverLetter) return;
    this.generatingCoverLetter = true;
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
        this.generatingCoverLetter = false;
      },
      complete: () => {
        this.generatingCoverLetter = false;
      },
    });
  }

  ratePositive() {
    this.job.feedback = this.job.feedback === 'positive' ? null : 'positive';
    const rating = this.job.feedback === 'positive' ? 1 : 0;
    this.jobService.submitFeedback(this.job.jobId, rating).subscribe();
  }

  rateNegative() {
    this.job.feedback = this.job.feedback === 'negative' ? null : 'negative';
    const rating = this.job.feedback === 'negative' ? -1 : 0;
    this.jobService.submitFeedback(this.job.jobId, rating).subscribe();
  }

  toggleSave() {
    this.job.saved = !this.job.saved;
    this.jobService.saveJob(this.job.jobId, this.job.saved).subscribe({
      error: () => {
        this.job.saved = !this.job.saved;
      },
    });
  }

  toggleApplied() {
    this.job.applied = !this.job.applied;
    this.jobService.applyJob(this.job.jobId, this.job.applied).subscribe({
      error: () => {
        this.job.applied = !this.job.applied;
      },
    });
  }
}
