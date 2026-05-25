import { Component, OnInit, OnDestroy } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Subscription, combineLatest } from 'rxjs';
import { Job } from '../../models/job.model';
import { Source } from '../../models/source.model';
import { JobService } from '../../services/job.service';
import { SourceService } from '../../services/source.service';
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
  filterMode: FilterMode = 'not-applied';
  showFeedbackForm = false;
  feedbackReasons: string[] = [];

  availableSources: Source[] = [];
  selectedSources: string[] = [];
  showSourceDropdown = false;

  private sub: Subscription | null = null;
  private routeSub: Subscription | null = null;
  private sourceSub: Subscription | null = null;

  allFeedbackReasons = [
    'Missing required skills',
    'Irrelevant location',
    'Salary expectations not met',
  ];

  constructor(
    private jobService: JobService,
    private sourceService: SourceService,
    private filterState: FilterStateService,
    private route: ActivatedRoute,
  ) {}

  ngOnInit() {
    this.sourceService.getSources().subscribe(res => {
      this.availableSources = res.data;
    });

    this.sourceSub = this.filterState.sources$.subscribe(sources => {
      this.selectedSources = sources;
    });

    this.sub = combineLatest([
      this.filterState.filterMode$,
      this.filterState.sources$,
    ]).subscribe(([mode, sources]) => {
      this.filterMode = mode;
      this.loadJobs(mode, sources);
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
    this.sourceSub?.unsubscribe();
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

  get isNotAppliedView(): boolean {
    return this.filterMode === 'not-applied';
  }

  get isInterestedView(): boolean {
    return this.filterMode === 'interested';
  }

  get isNotInterestedView(): boolean {
    return this.filterMode === 'not-interested';
  }

  toggleSource(sourceName: string) {
    this.filterState.toggleSource(sourceName);
  }

  isSourceSelected(sourceName: string): boolean {
    return this.selectedSources.includes(sourceName);
  }

  clearSources() {
    this.filterState.setSources([]);
  }

  private loadJobs(mode: FilterMode, sources: string[]) {
    this.loading = true;
    const applicable = mode === 'applicable' || mode === 'applied' ? true : undefined;
    const saved = mode === 'saved' ? true : undefined;
    const applied = mode === 'applied' ? true : mode === 'not-applied' ? false : undefined;
    const sourceParam = sources.length > 0 ? sources : undefined;
    this.jobService.getJobs(100, 0, applicable, saved, applied, sourceParam).subscribe({
      next: (res) => {
        let jobs = res.data;
        if (mode === 'not-applied') {
          jobs = jobs.filter(j => j.feedback !== 'negative' && !j.saved);
        } else if (mode === 'interested') {
          jobs = jobs.filter(j => j.feedback === 'positive');
        } else if (mode === 'not-interested') {
          jobs = jobs.filter(j => j.feedback === 'negative');
        }
        this.jobs = jobs;
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

  openAIRefinement(job: Job) {
    console.log('AI Refinement requested for:', job.title);
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
