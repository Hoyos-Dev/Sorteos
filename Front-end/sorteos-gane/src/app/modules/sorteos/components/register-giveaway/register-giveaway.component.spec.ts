import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RegisterGiveawayComponent } from './register-giveaway.component';

describe('RegisterGiveawayComponent', () => {
  let component: RegisterGiveawayComponent;
  let fixture: ComponentFixture<RegisterGiveawayComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [RegisterGiveawayComponent]
    });
    fixture = TestBed.createComponent(RegisterGiveawayComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});