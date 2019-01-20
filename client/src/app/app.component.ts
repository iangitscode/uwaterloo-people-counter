import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, timer } from 'rxjs';
import { switchMap, map } from 'rxjs/operators';

const API_URL:string = 'https://uwaterloo-people-counter.herokuapp.com'; //http://localhost:5000';
const FIVE_MINUTES_IN_MS: number = 1000 * 60 * 5;
const BUILDING_WHITELIST: string[] = [ "CIF", "CPH", "DC", "DWE", "E2", "E3", "E5", "E6", 
                                      "E7",  "EV1", "EV2", "EV3", "FED", "HH", "M3", "MC", 
                                      "PAS", "PAC", "QNC", "RAC", "RCH", "REN", "SCH", "SLC", 
                                      "STP", "TC", "UWP", "B1", "B2", "EC1", "EC2", "EC3", "EC4",
                                      "EC5", "BMH", "C2", "AL", "MKV" ];      

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
    })).pipe(map((data: any) => {
      return data.filter((obj: any) => {
        return BUILDING_WHITELIST.includes(obj.building_name);
      })
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
