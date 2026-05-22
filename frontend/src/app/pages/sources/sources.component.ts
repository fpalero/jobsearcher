import { Component, OnInit } from '@angular/core';
import { Source } from '../../models/source.model';
import { SourceService } from '../../services/source.service';

@Component({
  selector: 'app-sources',
  standalone: true,
  imports: [],
  templateUrl: './sources.component.html',
  styleUrl: './sources.component.css'
})
export class SourcesComponent implements OnInit {
  sources: Source[] = [];
  loading = true;
  syncPending: string | null = null;
  showConfirmModal = false;

  constructor(private sourceService: SourceService) {}

  ngOnInit() {
    this.loadSources();
  }

  loadSources() {
    this.loading = true;
    this.sourceService.getSources().subscribe({
      next: (res) => {
        this.sources = res.data;
        this.loading = false;
      },
      error: () => {
        this.loading = false;
      },
    });
  }

  triggerSync(sourceName: string) {
    this.syncPending = sourceName;
    this.showConfirmModal = true;
  }

  confirmSync() {
    if (!this.syncPending) return;
    const source = this.sources.find(s => s.name === this.syncPending);
    if (source) {
      source.status = 'syncing';
      source.progress = 0;
    }
    this.sourceService.startSync(this.syncPending).subscribe();
    this.showConfirmModal = false;
    this.syncPending = null;
  }

  cancelSyncModal() {
    this.showConfirmModal = false;
    this.syncPending = null;
  }

  stopSync(sourceName: string) {
    const source = this.sources.find(s => s.name === sourceName);
    if (source) {
      source.status = 'idle';
      source.progress = undefined;
    }
    this.sourceService.stopSync(sourceName).subscribe();
  }

  formatLastSync(lastSync: string | null): string {
    if (!lastSync) return 'Never';
    const date = new Date(lastSync);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  }
}
