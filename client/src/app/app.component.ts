import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, timer } from 'rxjs';
import { switchMap } from 'rxjs/operators';

const API_URL:string = 'https://uwaterloo-people-counter.herokuapp.com'; //http://localhost:5000';
const FIVE_MINUTES_IN_MS: number = 1000 * 60 * 5;

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.less']
})
export class AppComponent {
  private peopleCount: Observable<any>;
  constructor(private http: HttpClient) {
    this.peopleCount = timer(0, FIVE_MINUTES_IN_MS).pipe(switchMap(() => {
      return this.http.get(API_URL + "/peoplecount");
    }));
  }

  public getPeopleCount(): Observable<any> {
    return this.peopleCount;
  }

  public getBuildingName(obj: any): string {
    return obj.building_name;
  }

  public getNumPeople(obj: any): number {
    return obj.people_count;
  }
}
