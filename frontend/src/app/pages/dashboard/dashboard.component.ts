import { Component, OnInit, OnDestroy } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Subscription } from 'rxjs';
import { Job } from '../../models/job.model';
import { JobService } from '../../services/job.service';
import { FilterStateService, FilterMode } from '../../services/filter-state.service';
import { JobCardComponent } from '../../components/job-card/job-card.component';
import { JobDetailModalComponent } from '../../components/job-detail-modal/job-detail-modal.component';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [JobCardComponent, JobDetailModalComponent],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.css'
})
export class DashboardComponent implements OnInit, OnDestroy {
  jobs: Job[] = [];
  selectedJob: Job | null = null;
  loading = true;
  filterMode: FilterMode = 'all';
  showFeedbackForm = false;
  feedbackReasons: string[] = [];
  private sub: Subscription | null = null;
  private routeSub: Subscription | null = null;

  allFeedbackReasons = [
    'Missing required skills',
    'Irrelevant location',
    'Salary expectations not met',
  ];

  constructor(
    private jobService: JobService,
    private filterState: FilterStateService,
    private route: ActivatedRoute,
  ) {}

  ngOnInit() {
    this.sub = this.filterState.filterMode$.subscribe(mode => {
      this.filterMode = mode;
      this.loadJobs(mode);
    });
    this.routeSub = this.route.queryParams.subscribe(params => {
      const mode = params['mode'] as FilterMode | undefined;
      if (mode) {
        this.filterState.setMode(mode);
      }
    });
  }

  ngOnDestroy() {
    this.sub?.unsubscribe();
    this.routeSub?.unsubscribe();
  }

  get filterActive(): boolean {
    return this.filterMode === 'applicable' || this.filterMode === 'applied';
  }

  get isSavedView(): boolean {
    return this.filterMode === 'saved';
  }

  get isAppliedView(): boolean {
    return this.filterMode === 'applied';
  }

  private loadJobs(mode: FilterMode) {
    this.loading = true;
    const applicable = mode === 'applicable' || mode === 'applied' ? true : undefined;
    const saved = mode === 'saved' ? true : undefined;
    const applied = mode === 'applied' ? true : undefined;
    this.jobService.getJobs(100, 0, applicable, saved, applied).subscribe({
      next: (res) => {
        this.jobs = res.data;
        this.loading = false;
      },
      error: () => this.loading = false,
    });
  }

  showDetails(job: Job) {
    this.selectedJob = job;
  }

  closeDetails() {
    this.selectedJob = null;
  }

  toggleFeedbackReason(reason: string) {
    const idx = this.feedbackReasons.indexOf(reason);
    if (idx >= 0) {
      this.feedbackReasons.splice(idx, 1);
    } else {
      this.feedbackReasons.push(reason);
    }
  }

  submitFeedback() {
    this.showFeedbackForm = false;
    this.feedbackReasons = [];
  }

  cancelFeedback() {
    this.showFeedbackForm = false;
    this.feedbackReasons = [];
  }
}
