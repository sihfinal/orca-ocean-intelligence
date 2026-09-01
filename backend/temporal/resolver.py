"""
Temporal Expression Parsing & Resolution Engine for ORCA
ISRO SIH 2026 - Problem Statement 26176
Resolves relative and absolute temporal expressions into timezone-aware IST TimeWindows.
"""

import re
from datetime import datetime, timezone, timedelta
from typing import Optional, Tuple
from backend.temporal.models import TimeWindow, IST_OFFSET

class TemporalResolver:
    """
    Deterministic temporal reasoning component for marine queries.
    Parses natural language relative and absolute date/time expressions into IST TimeWindows.
    """
    MONTH_NAMES = {
        "january": 1, "jan": 1,
        "february": 2, "feb": 2,
        "march": 3, "mar": 3,
        "april": 4, "apr": 4,
        "may": 5,
        "june": 6, "jun": 6,
        "july": 7, "jul": 7,
        "august": 8, "aug": 8,
        "september": 9, "sep": 9, "sept": 9,
        "october": 10, "oct": 10,
        "november": 11, "nov": 11,
        "december": 12, "dec": 12
    }

    DAY_NAMES = {
        "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
        "friday": 4, "saturday": 5, "sunday": 6
    }

    def __init__(self, reference_time: Optional[datetime] = None):
        self._reference_time = reference_time

    def get_current_time(self) -> datetime:
        """Returns the current IST datetime."""
        if self._reference_time:
            if self._reference_time.tzinfo is None:
                return self._reference_time.replace(tzinfo=IST_OFFSET)
            return self._reference_time.astimezone(IST_OFFSET)
        return datetime.now(IST_OFFSET)

    def resolve(self, query: str) -> Optional[TimeWindow]:
        """
        Extracts and resolves temporal expressions from the query text.
        Returns a structured TimeWindow or None if no temporal expression is present.
        """
        if not query:
            return None

        q = query.lower().strip()
        now = self.get_current_time()
        today_date = now.date()

        # ----------------------------------------------------
        # 1. Specific Time Range: "between X and Y tomorrow" or "from X to Y"
        # ----------------------------------------------------
        range_match = re.search(r'(?:between|from)\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?\s*(?:and|to)\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?(?:\s+(tomorrow|today))?', q)
        if range_match:
            h1 = int(range_match.group(1))
            m1 = int(range_match.group(2) or 0)
            ampm1 = range_match.group(3)
            h2 = int(range_match.group(4))
            m2 = int(range_match.group(5) or 0)
            ampm2 = range_match.group(6) or ampm1  # propagate am/pm if omitted
            day_target = range_match.group(7)

            if ampm1 == "pm" and h1 < 12: h1 += 12
            elif ampm1 == "am" and h1 == 12: h1 = 0
            if ampm2 == "pm" and h2 < 12: h2 += 12
            elif ampm2 == "am" and h2 == 12: h2 = 0

            # Validate hour/minute
            if 0 <= h1 <= 24 and 0 <= h2 <= 24 and 0 <= m1 < 60 and 0 <= m2 < 60:
                target_date = today_date + timedelta(days=1) if day_target == "tomorrow" else today_date
                try:
                    start_dt = datetime(target_date.year, target_date.month, target_date.day, h1 % 24, m1, tzinfo=IST_OFFSET)
                    end_dt = datetime(target_date.year, target_date.month, target_date.day, h2 % 24, m2, tzinfo=IST_OFFSET)
                    if end_dt > start_dt:
                        return TimeWindow(
                            start_datetime=start_dt,
                            end_datetime=end_dt,
                            label=f"range_{start_dt.strftime('%H:%M')}_to_{end_dt.strftime('%H:%M')}",
                            is_relative=True,
                            is_future=start_dt > now,
                            resolution_source="explicit_time_range",
                            data_type="FORECAST" if start_dt > now else "OBSERVED",
                            forecast_executable=False,
                            capability_note="Time range understood. Future forecast execution deferred to Phase 4."
                        )
                except ValueError:
                    pass

        # ----------------------------------------------------
        # 2. Specific Date Expressions: e.g. "15 September 2026", "15-09-2026", "2026-09-15"
        # ----------------------------------------------------
        # Pattern A: "15 September 2026" or "15 September"
        date_word_match = re.search(r'\b(\d{1,2})(?:st|nd|rd|th)?\s+(january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sep|sept|oct|nov|dec)\b(?:\s+(\d{4}))?', q)
        if date_word_match:
            d = int(date_word_match.group(1))
            m_str = date_word_match.group(2)
            y = int(date_word_match.group(3) or today_date.year)
            m = self.MONTH_NAMES.get(m_str)

            # Check optional time of day (e.g. "morning", "06:00")
            time_match = re.search(r'\b(\d{1,2}):(\d{2})\b', q)
            part_match = re.search(r'\b(morning|afternoon|evening|night)\b', q)

            try:
                if time_match:
                    th = int(time_match.group(1))
                    tm = int(time_match.group(2))
                    start_dt = datetime(y, m, d, th, tm, tzinfo=IST_OFFSET)
                    end_dt = start_dt + timedelta(hours=2)
                elif part_match:
                    p = part_match.group(1)
                    if p == "morning": start_dt, end_dt = datetime(y, m, d, 6, 0, tzinfo=IST_OFFSET), datetime(y, m, d, 12, 0, tzinfo=IST_OFFSET)
                    elif p == "afternoon": start_dt, end_dt = datetime(y, m, d, 12, 0, tzinfo=IST_OFFSET), datetime(y, m, d, 17, 0, tzinfo=IST_OFFSET)
                    elif p == "evening": start_dt, end_dt = datetime(y, m, d, 17, 0, tzinfo=IST_OFFSET), datetime(y, m, d, 21, 0, tzinfo=IST_OFFSET)
                    else: start_dt, end_dt = datetime(y, m, d, 21, 0, tzinfo=IST_OFFSET), datetime(y, m, d, 23, 59, tzinfo=IST_OFFSET)
                else:
                    start_dt = datetime(y, m, d, 0, 0, tzinfo=IST_OFFSET)
                    end_dt = datetime(y, m, d, 23, 59, 59, tzinfo=IST_OFFSET)

                is_future = start_dt > now
                return TimeWindow(
                    start_datetime=start_dt,
                    end_datetime=end_dt,
                    label=f"date_{y}_{m:02d}_{d:02d}",
                    is_relative=False,
                    is_future=is_future,
                    resolution_source="calendar_date",
                    data_type="FORECAST" if is_future else "OBSERVED",
                    forecast_executable=False,
                    capability_note="Calendar date understood. Historical/forecast feeds deferred to Phase 4."
                )
            except ValueError:
                # Malformed date (e.g. 31 February)
                return None

        # ----------------------------------------------------
        # 3. Relative Days: "tomorrow morning", "tomorrow evening", "tomorrow", "tonight", "today"
        # ----------------------------------------------------
        # Tomorrow combinations
        if "tomorrow" in q or "kal" in q or "naale" in q:
            target_date = today_date + timedelta(days=1)
            if "morning" in q or "subah" in q or "bellagge" in q:
                start_dt = datetime(target_date.year, target_date.month, target_date.day, 6, 0, tzinfo=IST_OFFSET)
                end_dt = datetime(target_date.year, target_date.month, target_date.day, 12, 0, tzinfo=IST_OFFSET)
                label = "tomorrow_morning"
            elif "afternoon" in q or "dopahar" in q:
                start_dt = datetime(target_date.year, target_date.month, target_date.day, 12, 0, tzinfo=IST_OFFSET)
                end_dt = datetime(target_date.year, target_date.month, target_date.day, 17, 0, tzinfo=IST_OFFSET)
                label = "tomorrow_afternoon"
            elif "evening" in q or "shaam" in q or "sanje" in q:
                start_dt = datetime(target_date.year, target_date.month, target_date.day, 17, 0, tzinfo=IST_OFFSET)
                end_dt = datetime(target_date.year, target_date.month, target_date.day, 21, 0, tzinfo=IST_OFFSET)
                label = "tomorrow_evening"
            elif "night" in q or "raat" in q:
                start_dt = datetime(target_date.year, target_date.month, target_date.day, 21, 0, tzinfo=IST_OFFSET)
                end_dt = datetime(target_date.year, target_date.month, target_date.day, 23, 59, 59, tzinfo=IST_OFFSET)
                label = "tomorrow_night"
            else:
                start_dt = datetime(target_date.year, target_date.month, target_date.day, 6, 0, tzinfo=IST_OFFSET)
                end_dt = datetime(target_date.year, target_date.month, target_date.day, 18, 0, tzinfo=IST_OFFSET)
                label = "tomorrow_full_day"

            return TimeWindow(
                start_datetime=start_dt,
                end_datetime=end_dt,
                label=label,
                is_relative=True,
                is_future=True,
                resolution_source="relative_tomorrow",
                data_type="FORECAST",
                forecast_executable=False,
                capability_note="Tomorrow window understood. Predictive ocean state forecast model deferred to Phase 4."
            )

        # Yesterday
        if "yesterday" in q:
            target_date = today_date - timedelta(days=1)
            start_dt = datetime(target_date.year, target_date.month, target_date.day, 0, 0, tzinfo=IST_OFFSET)
            end_dt = datetime(target_date.year, target_date.month, target_date.day, 23, 59, 59, tzinfo=IST_OFFSET)
            return TimeWindow(
                start_datetime=start_dt,
                end_datetime=end_dt,
                label="yesterday",
                is_relative=True,
                is_future=False,
                resolution_source="relative_yesterday",
                data_type="HISTORICAL",
                forecast_executable=False,
                capability_note="Past temporal window understood. Historical telemetry store deferred to Phase 5."
            )

        # Today / Tonight / Current Day Parts
        if any(k in q for k in ["today", "tonight", "this morning", "this evening", "this afternoon", "aaj"]):
            if "morning" in q or "this morning" in q:
                start_dt = datetime(today_date.year, today_date.month, today_date.day, 6, 0, tzinfo=IST_OFFSET)
                end_dt = datetime(today_date.year, today_date.month, today_date.day, 12, 0, tzinfo=IST_OFFSET)
                label = "today_morning"
            elif "afternoon" in q:
                start_dt = datetime(today_date.year, today_date.month, today_date.day, 12, 0, tzinfo=IST_OFFSET)
                end_dt = datetime(today_date.year, today_date.month, today_date.day, 17, 0, tzinfo=IST_OFFSET)
                label = "today_afternoon"
            elif "evening" in q or "this evening" in q:
                start_dt = datetime(today_date.year, today_date.month, today_date.day, 17, 0, tzinfo=IST_OFFSET)
                end_dt = datetime(today_date.year, today_date.month, today_date.day, 21, 0, tzinfo=IST_OFFSET)
                label = "today_evening"
            elif "tonight" in q:
                start_dt = datetime(today_date.year, today_date.month, today_date.day, 21, 0, tzinfo=IST_OFFSET)
                end_dt = datetime(today_date.year, today_date.month, today_date.day, 23, 59, 59, tzinfo=IST_OFFSET)
                label = "tonight"
            else:
                start_dt = datetime(today_date.year, today_date.month, today_date.day, 0, 0, tzinfo=IST_OFFSET)
                end_dt = datetime(today_date.year, today_date.month, today_date.day, 23, 59, 59, tzinfo=IST_OFFSET)
                label = "today"

            is_future = start_dt > now
            return TimeWindow(
                start_datetime=start_dt,
                end_datetime=end_dt,
                label=label,
                is_relative=True,
                is_future=is_future,
                resolution_source="relative_today",
                data_type="FORECAST" if is_future else "OBSERVED",
                forecast_executable=not is_future,
                capability_note="Current day window parsed."
            )

        # Next Week / Next Day-of-week (e.g. "next Monday")
        next_day_match = re.search(r'\bnext\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b', q)
        if next_day_match:
            target_dow = self.DAY_NAMES.get(next_day_match.group(1))
            current_dow = today_date.weekday()
            days_ahead = (target_dow - current_dow) % 7
            if days_ahead == 0:
                days_ahead = 7
            target_date = today_date + timedelta(days=days_ahead)
            start_dt = datetime(target_date.year, target_date.month, target_date.day, 6, 0, tzinfo=IST_OFFSET)
            end_dt = datetime(target_date.year, target_date.month, target_date.day, 18, 0, tzinfo=IST_OFFSET)
            return TimeWindow(
                start_datetime=start_dt,
                end_datetime=end_dt,
                label=f"next_{next_day_match.group(1)}",
                is_relative=True,
                is_future=True,
                resolution_source="next_day_of_week",
                data_type="FORECAST",
                forecast_executable=False,
                capability_note="Next day-of-week understood. Long-range forecast model deferred to Phase 4."
            )

        # Now / Currently / Right now
        if any(k in q for k in ["now", "currently", "at present", "right now", "live"]):
            return TimeWindow(
                start_datetime=now,
                end_datetime=now + timedelta(hours=1),
                label="current_realtime",
                is_relative=True,
                is_future=False,
                resolution_source="realtime_clock",
                data_type="OBSERVED",
                forecast_executable=True,
                capability_note="Real-time observation window active."
            )

        return None
