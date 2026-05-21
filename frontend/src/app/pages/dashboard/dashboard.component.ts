import { Component, OnInit, OnDestroy } from '@angular/core';
import { Subscription } from 'rxjs';
import { Job } from '../../models/job.model';
import { JobService } from '../../services/job.service';
import { FilterStateService } from '../../services/filter-state.service';
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
  filterActive = false;
  private sub: Subscription | null = null;

  constructor(
    private jobService: JobService,
    private filterState: FilterStateService,
  ) {}

  ngOnInit() {
    this.sub = this.filterState.applicable$.subscribe(applicable => {
      this.filterActive = applicable === true;
      this.loadJobs(applicable);
    });
  }

  ngOnDestroy() {
    this.sub?.unsubscribe();
  }

  private loadJobs(applicable?: boolean) {
    this.loading = true;
    this.jobService.getJobs(100, 0, applicable).subscribe({
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
}
