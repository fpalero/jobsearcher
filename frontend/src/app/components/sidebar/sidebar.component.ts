import { Component, OnInit, OnDestroy } from '@angular/core';
import { Router, RouterModule } from '@angular/router';
import { Subscription } from 'rxjs';
import { FilterStateService } from '../../services/filter-state.service';
import { JobService, JobCounts } from '../../services/job.service';

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [RouterModule],
  templateUrl: './sidebar.component.html',
  styleUrl: './sidebar.component.css'
})
export class SidebarComponent implements OnInit, OnDestroy {
  activeItem = 'not-applied';
  counts: JobCounts = { total: 0, available: 0, applied: 0, saved: 0, interested: 0, not_interested: 0 };
  private sub: Subscription | null = null;

  constructor(
    private filterState: FilterStateService,
    private router: Router,
    private jobService: JobService,
  ) {}

  ngOnInit() {
    this.loadCounts();

    this.sub = this.filterState.filterMode$.subscribe(mode => {
      if (mode === 'saved') this.activeItem = 'saved';
      else if (mode === 'applied') this.activeItem = 'applied';
      else if (mode === 'not-applied') this.activeItem = 'not-applied';
      else if (mode === 'all') this.activeItem = 'all-jobs';
      else if (mode === 'interested') this.activeItem = 'interested';
      else if (mode === 'not-interested') this.activeItem = 'not-interested';
      else this.activeItem = 'not-applied';
      this.loadCounts();
    });

    this.router.events.subscribe(() => {
      const url = this.router.url;
      if (url.startsWith('/sources')) {
        this.activeItem = 'sources';
      }
    });
  }

  ngOnDestroy() {
    this.sub?.unsubscribe();
  }

  private loadCounts() {
    this.jobService.getCounts().subscribe(c => this.counts = c);
  }

  showAllJobs() {
    this.filterState.setMode('not-applied');
  }

  showApplied() {
    this.filterState.setMode('applied');
  }

  showSaved() {
    this.filterState.setMode('saved');
  }

  showInterested() {
    this.filterState.setFeedbackMode('interested');
  }

  showNotInterested() {
    this.filterState.setFeedbackMode('not-interested');
  }
}
