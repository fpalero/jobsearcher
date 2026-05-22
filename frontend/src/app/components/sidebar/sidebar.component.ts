import { Component, OnInit } from '@angular/core';
import { RouterModule } from '@angular/router';
import { FilterStateService } from '../../services/filter-state.service';

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [RouterModule],
  templateUrl: './sidebar.component.html',
  styleUrl: './sidebar.component.css'
})
export class SidebarComponent implements OnInit {
  activeItem = 'all-jobs';

  constructor(private filterState: FilterStateService) {}

  ngOnInit() {
    this.filterState.applicable$.subscribe(val => {
      this.activeItem = val === true ? 'applied' : 'all-jobs';
    });
    this.filterState.filterMode$.subscribe(mode => {
      if (mode === 'saved') this.activeItem = 'saved';
      else if (mode === 'applied') this.activeItem = 'applied';
      else if (mode === 'all') this.activeItem = 'all-jobs';
    });
  }

  showAllJobs() {
    this.filterState.setMode('all');
  }

  showApplied() {
    this.filterState.setMode('applied');
  }

  showSaved() {
    this.filterState.setMode('saved');
  }
}
