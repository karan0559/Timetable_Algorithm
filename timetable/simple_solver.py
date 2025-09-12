import json
import random
from typing import Dict, List, Set, Tuple
from collections import defaultdict

class SimpleTimetableSolver:
    def __init__(self):
        """Initialize solver state and configuration."""
        # ---------------- Core data structures ----------------
        self.training_data = None
        self.scheduled_slots = defaultdict(list)    # day -> list (legacy)
        self.faculty_schedule = defaultdict(set)    # faculty -> set(slot_keys)
        self.room_schedule = defaultdict(set)       # room -> set(slot_keys)
        self.course_schedule = defaultdict(set)     # slot_key -> set(courses) for student conflict detection
        self.global_slot_usage = set()              # slot_keys already occupied (single course per slot)
        self.day_load = defaultdict(int)            # day -> count of sessions
        self.faculty_day_load = defaultdict(int)    # (faculty, day) -> count

        # ---------------- Policy / tuning constants ----------------
        self.MAX_FACULTY_SESSIONS_PER_DAY = 5        # Hard per-faculty cap (relaxed if needed)
        self.PREFERRED_FACULTY_SESSIONS_PER_DAY = 3  # Soft distribution target
        self.allow_parallel = True                   # Allow multiple courses same slot (disables global single-slot restriction)
        self.default_lab_session_length = 2          # Default contiguous hours per lab block

        # ---------------- Tracking for validation & diagnostics ----------------
        self.expected_weekly: Dict[str, int] = {}     # course -> weekly_count expected
        self.actual_weekly = defaultdict(int)         # course -> actual scheduled occurrences
        self.failure_reasons: Dict[str, str] = {}     # course -> reason code string

        # ---------------- Canonical ordering ----------------
        self.days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        self.time_slots = [
            '09:00-10:00', '10:00-11:00', '11:00-12:00', '12:00-13:00',
            '13:00-14:00', '14:00-15:00', '15:00-16:00', '16:00-17:00', '17:00-18:00'
        ]

        # ---------------- Student conflict groups (shared cohorts) ----------------
        self.core_courses = {
            'computer_science': [
                'data structures', 'software engineering', 'computer networks',
                'database systems', 'algorithms', 'operating systems',
                'computer graphics', 'machine learning', 'artificial intelligence'
            ],
            'information_technology': [
                'data structures', 'database systems', 'computer networks',
                'web development', 'software engineering', 'cyber security'
            ]
        }

        # ---------------- Slot & day mappings (legacy support) ----------------
        self.slot_mapping = {
            '1': '09:00-10:00', '2': '10:00-11:00', '3': '11:00-12:00', '4': '12:00-13:00',
            '5': '13:00-14:00', '6': '14:00-15:00', '7': '15:00-16:00', '8': '16:00-17:00', '9': '17:00-18:00'
        }
        self.day_mapping = {
            'Mon': 'Monday', 'Tue': 'Tuesday', 'Wed': 'Wednesday',
            'Thu': 'Thursday', 'Fri': 'Friday'
        }
        
    def load_training_data(self, file_path: str = './data/training_dataset.json'):
        """Load training data from JSON file."""
        try:
            with open(file_path, 'r') as f:
                self.training_data = json.load(f)
            print(f"✅ Loaded training data: {self.training_data['metadata']['total_courses']} courses")
            return True
        except FileNotFoundError:
            print(f"❌ Training data file not found: {file_path}")
            return False
        except Exception as e:
            print(f"❌ Error loading training data: {str(e)}")
            return False
    
    def parse_availability_slots(self, availability_data):
        """Parse availability string into (day, time_slot) tuples.
        Enhanced to generate ALL time slots for available days.
        """
        if not availability_data:
            return []
        
        # Handle both string and list formats
        if isinstance(availability_data, list):
            availability_str = ','.join(str(slot) for slot in availability_data)
        else:
            availability_str = str(availability_data)
            
        slots = []
        
        # Define all available time slots throughout the day
        all_time_slots = [
            '09:00-10:00', '10:00-11:00', '11:00-12:00', '12:00-13:00',
            '13:00-14:00', '14:00-15:00', '15:00-16:00', '16:00-17:00', '17:00-18:00'
        ]
        
        # Enhanced day mapping
        day_mapping = {
            'monday': 'Monday', 'tuesday': 'Tuesday', 'wednesday': 'Wednesday',
            'thursday': 'Thursday', 'friday': 'Friday',
            'mon': 'Monday', 'tue': 'Tuesday', 'wed': 'Wednesday',
            'thu': 'Thursday', 'fri': 'Friday'
        }
        
        for slot in availability_str.split(','):
            slot = slot.strip().lower()
            if not slot:
                continue
            
            # Check if it's a day name (e.g., "Monday", "Tuesday")
            if slot in day_mapping:
                day = day_mapping[slot]
                # 🎯 KEY FIX: Generate ALL time slots for this day
                for time_slot in all_time_slots:
                    slots.append((day, time_slot))
                continue
            
            # Handle specific time formats if provided
            if ' ' in slot:
                parts = slot.split()
                day_part = parts[0]
                time_part = ' '.join(parts[1:])
                
                if day_part in day_mapping:
                    day = day_mapping[day_part]
                    # Map specific time if provided
                    time_map = {
                        '9am': '09:00-10:00', '10am': '10:00-11:00', '11am': '11:00-12:00', 
                        '12pm': '12:00-13:00', '2pm': '14:00-15:00', '3pm': '15:00-16:00', 
                        '4pm': '16:00-17:00', '5pm': '17:00-18:00'
                    }
                    
                    if time_part in time_map:
                        slots.append((day, time_map[time_part]))
                    else:
                        # If time format not recognized, give all slots for that day
                        for time_slot in all_time_slots:
                            slots.append((day, time_slot))
                continue
            
            # Handle abbreviated formats
            if len(slot) <= 4 and any(c.isalpha() for c in slot):
                day_part = ''.join([c for c in slot if c.isalpha()])
                
                if day_part in day_mapping:
                    day = day_mapping[day_part]
                    # Generate all time slots for this day
                    for time_slot in all_time_slots:
                        slots.append((day, time_slot))
                
        return slots
    
    def is_slot_available(self, day: str, time_slot: str, faculty: str, room: str) -> bool:
        """Check if a specific slot is available for faculty and room."""
        slot_key = f"{day}_{time_slot}"
        # Global single-course constraint unless parallel allowed
        if not self.allow_parallel and slot_key in self.global_slot_usage:
            return False
        # Check if faculty is busy
        if slot_key in self.faculty_schedule[faculty]:
            return False
            
        # Check if room is busy
        if slot_key in self.room_schedule[room]:
            return False
            
        return True
    
    def has_student_conflict(self, day: str, time_slot: str, course_name: str) -> bool:
        """Check if scheduling this course would create a student conflict."""
        slot_key = f"{day}_{time_slot}"
        
        # Get courses already scheduled at this time
        if slot_key in self.course_schedule:
            existing_courses = self.course_schedule[slot_key]
            
            # Check if any existing course conflicts with the new course
            for existing_course in existing_courses:
                if self._courses_conflict(course_name.lower(), existing_course.lower()):
                    return True
                    
        return False
    
    def _courses_conflict(self, course1: str, course2: str) -> bool:
        """Check if two courses are likely to be taken by the same students."""
        base1 = self._normalize_course_name(course1)
        base2 = self._normalize_course_name(course2)
        if base1 == base2:
            return False  # Same course (lecture/lab) shouldn't count as student conflict
        for _, courses in self.core_courses.items():
            if base1 in courses and base2 in courses:
                return True
        return False

    def _normalize_course_name(self, name: str) -> str:
        """Strip session qualifiers like '(lecture)' or '(lab)' and normalize spacing/case."""
        n = name.lower().strip()
        # Remove parentheses qualifiers
        if '(' in n and ')' in n:
            n = n[:n.index('(')].strip()
        return n
    
    def schedule_course(self, course_info: Dict, available_slots: List[Tuple[str, str]]) -> bool:
        """Try to schedule a course with enhanced conflict prevention."""
        import random
        
        course_name = course_info['course']
        faculty = course_info['faculty']
        room = course_info['room']
        duration = course_info.get('duration', 1)
        session_type = course_info.get('session_type', 'lecture')
        
        print(f"🔍 Scheduling {course_name}: faculty={faculty}, room={room}, duration={duration}, type={session_type}")
        print(f"   Available slots: {available_slots}")
        
        # Handle lab sessions differently (may require multiple contiguous blocks)
        if session_type == 'lab':
            return self._schedule_lab_sessions(course_info, available_slots)
        else:
            return self._schedule_lecture_sessions(course_info, available_slots)
    
    def _schedule_lab_sessions(self, course_info: Dict, available_slots: List[Tuple[str, str]]) -> bool:
        """Schedule required lab blocks (each contiguous). Tracks each hour toward weekly count."""
        course_name = course_info['course']
        faculty = course_info['faculty']
        room = course_info['room']
        weekly_count = course_info.get('weekly_count', 1)
        block_hours = course_info.get('lab_duration', self.default_lab_session_length)

        # Organize candidate slots by day
        day_slots = defaultdict(list)
        for d, ts in available_slots:
            day_slots[d].append(ts)
        for d in day_slots:
            day_slots[d].sort(key=lambda x: self._get_time_index(x))

        blocks_scheduled = 0
        used_days = set()
        days_order = sorted(day_slots.keys(), key=lambda d: (self.day_load[d], d))
        # Attempt until blocks_scheduled * block_hours >= weekly_count * block_hours (treat weekly_count as number of blocks)
        target_blocks = weekly_count
        while blocks_scheduled < target_blocks:
            progress = False
            for day in days_order:
                if blocks_scheduled >= target_blocks:
                    break
                # Distinct-day preference when enough days exist
                if len(days_order) >= target_blocks and day in used_days:
                    continue
                times = day_slots[day]
                for i in range(len(times)):
                    candidate = times[i:i+block_hours]
                    if len(candidate) < block_hours:
                        break
                    # Check consecutiveness
                    base_idx = self._get_time_index(candidate[0])
                    if any(self._get_time_index(candidate[j]) != base_idx + j for j in range(block_hours)):
                        continue
                    # Check availability for entire block
                    if any((not self.is_slot_available(day, ts, faculty, room) or self.has_student_conflict(day, ts, course_name)) for ts in candidate):
                        continue
                    # Schedule block
                    for ts in candidate:
                        slot_key = f"{day}_{ts}"
                        self.faculty_schedule[faculty].add(slot_key)
                        self.room_schedule[room].add(slot_key)
                        if not self.allow_parallel:
                            self.global_slot_usage.add(slot_key)
                        self.day_load[day] += 1
                        self.faculty_day_load[(faculty, day)] += 1
                        if slot_key not in self.course_schedule:
                            self.course_schedule[slot_key] = set()
                        self.course_schedule[slot_key].add(course_name)
                        if day not in self.scheduled_slots:
                            self.scheduled_slots[day] = {}
                        if ts not in self.scheduled_slots[day]:
                            self.scheduled_slots[day][ts] = []
                        self.scheduled_slots[day][ts].append({
                            'course': course_name,
                            'faculty': faculty,
                            'room': room,
                            'duration': block_hours,
                            'session_type': 'lab'
                        })
                        self.actual_weekly[course_name] += 1  # count each hour; alternative: count block separately
                    blocks_scheduled += 1
                    used_days.add(day)
                    progress = True
                    print(f"   ✅ Scheduled lab block ({block_hours}h) on {day}: {candidate}")
                    break
            if not progress:
                self.failure_reasons[course_name] = 'LAB_NO_BLOCK'
                print(f"   ❌ Could not schedule all lab blocks for {course_name}")
                return blocks_scheduled > 0
        return True
    
    def _select_lecture_slots_diverse(self, course_name: str, faculty: str, valid_slots: List[Tuple[str, str]], needed: int) -> List[Tuple[str, str]]:
        """Improved slot selection:
        - One session per distinct day before repeating.
        - Prefer globally light days & days where faculty has fewer sessions.
        - Enforce a faculty per-day cap (soft/hard) then relax if insufficient.
        - Time preference ordering preserved.
        """
        if needed <= 0 or not valid_slots:
            return []
        from collections import defaultdict as _dd
        day_to_times = _dd(list)
        for d, ts in valid_slots:
            day_to_times[d].append(ts)
        pref = ['10:00-11:00','11:00-12:00','09:00-10:00','14:00-15:00','15:00-16:00','13:00-14:00','16:00-17:00','12:00-13:00','17:00-18:00']
        def tscore(t):
            return pref.index(t) if t in pref else len(pref)
        for d in day_to_times:
            day_to_times[d].sort(key=tscore)
        chosen: List[Tuple[str,str]] = []
        hard_cap = self.MAX_FACULTY_SESSIONS_PER_DAY
        def day_key(day:str):
            return (self.day_load[day], self.faculty_day_load[(faculty, day)], day)
        def pick(day:str):
            for ts in day_to_times[day]:
                if (day, ts) in chosen:
                    continue
                if self.faculty_day_load[(faculty, day)] >= hard_cap:
                    continue
                return (day, ts)
            return None
        ordered_days = sorted(day_to_times.keys(), key=day_key)
        # Pass 1 distinct days
        for d in ordered_days:
            if len(chosen) >= needed:
                break
            slot = pick(d)
            if slot:
                chosen.append(slot)
        # Pass 2 fill with remaining respecting caps
        relax_attempts = 0
        while len(chosen) < needed and relax_attempts < 3:
            for d in ordered_days:
                if len(chosen) >= needed:
                    break
                slot = pick(d)
                if slot:
                    chosen.append(slot)
            if len(chosen) < needed:
                hard_cap += 1  # Relax cap
            relax_attempts += 1
        return chosen[:needed]

    # ---------------- Iterative single-session scheduling helpers ----------------
    def _schedule_one_lecture_session(self, state: Dict) -> bool:
        """Schedule one lecture session for a course state (greedy diversified)."""
        course = state['name']
        faculty = state['faculty']
        room = state['room']
        # Build valid slots
        valid = []
        for day, ts in state['available_slots']:
            if (self.is_slot_available(day, ts, faculty, room) and not self.has_student_conflict(day, ts, course)):
                valid.append((day, ts))
        if not valid:
            return False
        # Prefer day with lowest load and faculty day load; then time preference
        def score(slot):
            d, t = slot
            return (self.day_load[d], self.faculty_day_load[(faculty, d)], self._get_time_preference(t))
        valid.sort(key=score)
        day, ts = valid[0]
        slot_key = f"{day}_{ts}"
        self.faculty_schedule[faculty].add(slot_key)
        self.room_schedule[room].add(slot_key)
        if not self.allow_parallel:
            self.global_slot_usage.add(slot_key)
        self.day_load[day] += 1
        self.faculty_day_load[(faculty, day)] += 1
        if slot_key not in self.course_schedule:
            self.course_schedule[slot_key] = set()
        self.course_schedule[slot_key].add(course)
        if day not in self.scheduled_slots:
            self.scheduled_slots[day] = {}
        if ts not in self.scheduled_slots[day]:
            self.scheduled_slots[day][ts] = []
        self.scheduled_slots[day][ts].append({
            'course': course,
            'faculty': faculty,
            'room': room,
            'duration': 1,
            'session_type': 'lecture'
        })
        self.actual_weekly[course] += 1
        return True

    def _schedule_one_lab_block(self, state: Dict) -> bool:
        """Schedule one contiguous lab block (default length) for a lab course state."""
        course = state['name']
        faculty = state['faculty']
        room = state['room']
        block_hours = self.default_lab_session_length
        # Organize by day
        day_slots = defaultdict(list)
        for d, ts in state['available_slots']:
            day_slots[d].append(ts)
        for d in day_slots:
            day_slots[d].sort(key=lambda x: self._get_time_index(x))
        # Candidate days ordered by load
        ordered_days = sorted(day_slots.keys(), key=lambda d: (self.day_load[d], self.faculty_day_load[(faculty, d)], d))
        for day in ordered_days:
            times = day_slots[day]
            for i in range(len(times)):
                segment = times[i:i+block_hours]
                if len(segment) < block_hours:
                    break
                base = self._get_time_index(segment[0])
                if any(self._get_time_index(segment[j]) != base + j for j in range(block_hours)):
                    continue
                if any((not self.is_slot_available(day, ts, faculty, room) or self.has_student_conflict(day, ts, course)) for ts in segment):
                    continue
                # schedule
                for ts in segment:
                    slot_key = f"{day}_{ts}"
                    self.faculty_schedule[faculty].add(slot_key)
                    self.room_schedule[room].add(slot_key)
                    if not self.allow_parallel:
                        self.global_slot_usage.add(slot_key)
                    self.day_load[day] += 1
                    self.faculty_day_load[(faculty, day)] += 1
                    if slot_key not in self.course_schedule:
                        self.course_schedule[slot_key] = set()
                    self.course_schedule[slot_key].add(course)
                    if day not in self.scheduled_slots:
                        self.scheduled_slots[day] = {}
                    if ts not in self.scheduled_slots[day]:
                        self.scheduled_slots[day][ts] = []
                    self.scheduled_slots[day][ts].append({
                        'course': course,
                        'faculty': faculty,
                        'room': room,
                        'duration': block_hours,
                        'session_type': 'lab'
                    })
                    self.actual_weekly[course] += 1  # counting hours
                return True
        # No block
        return False

    def _schedule_lecture_sessions(self, course_info: Dict, available_slots: List[Tuple[str, str]]) -> bool:
        """Schedule lecture sessions (3 separate 1-hour slots)."""
        course_name = course_info['course']
        faculty = course_info['faculty']
        room = course_info['room']
        duration = course_info.get('duration', 3)  # 3 lectures per week
        
        # Find available slots for lectures
        valid_slots = []
        for day, time_slot in available_slots:
            if (self.is_slot_available(day, time_slot, faculty, room) and 
                not self.has_student_conflict(day, time_slot, course_name)):
                valid_slots.append((day, time_slot))
        
        print(f"   Valid lecture slots after conflict check: {valid_slots}")
        
        if len(valid_slots) >= duration:
            # Select optimal slots for lectures
            selected_slots = self._select_lecture_slots_diverse(course_name, faculty, valid_slots, duration)
            
            # Schedule all lecture slots
            for day, time_slot in selected_slots:
                slot_key = f"{day}_{time_slot}"
                
                # Mark faculty and room as busy
                self.faculty_schedule[faculty].add(slot_key)
                self.room_schedule[room].add(slot_key)
                self.global_slot_usage.add(slot_key)
                self.day_load[day] += 1
                self.faculty_day_load[(faculty, day)] += 1
                
                # Track course scheduling for student conflict prevention
                if slot_key not in self.course_schedule:
                    self.course_schedule[slot_key] = set()
                self.course_schedule[slot_key].add(course_name)
                
                # Add to timetable
                if day not in self.scheduled_slots:
                    self.scheduled_slots[day] = {}
                if time_slot not in self.scheduled_slots[day]:
                    self.scheduled_slots[day][time_slot] = []
                    
                self.scheduled_slots[day][time_slot].append({
                    'course': course_name,
                    'faculty': faculty,
                    'room': room,
                    'duration': 1,
                    'session_type': 'lecture'
                })
                self.actual_weekly[course_name] += 1
            
            print(f"   ✅ Successfully scheduled diversified lectures: {selected_slots}")
            return True
        else:
            print(f"   ❌ Not enough valid slots for lectures (need {duration}, have {len(valid_slots)})")
            self.failure_reasons[course_name] = 'LECTURE_INSUFFICIENT_SLOTS'
            return False
    
    def _find_consecutive_pairs(self, available_slots: List[Tuple[str, str]], faculty: str, room: str, course_name: str) -> List[List[Tuple[str, str]]]:
        """Find consecutive 2-hour slots for lab sessions."""
        # Group by day
        days_slots = {}
        for day, time_slot in available_slots:
            if day not in days_slots:
                days_slots[day] = []
            days_slots[day].append(time_slot)
        
        consecutive_pairs = []
        
        # Look for consecutive pairs on each day
        for day, time_slots in days_slots.items():
            time_slots.sort(key=lambda x: self._get_time_index(x))
            
            # Check each possible consecutive pair
            for i in range(len(time_slots) - 1):
                time1 = time_slots[i]
                time2 = time_slots[i + 1]
                
                # Check if they are consecutive
                if self._get_time_index(time2) == self._get_time_index(time1) + 1:
                    # Check if both slots are available and conflict-free
                    if (self.is_slot_available(day, time1, faculty, room) and
                        self.is_slot_available(day, time2, faculty, room) and
                        not self.has_student_conflict(day, time1, course_name) and
                        not self.has_student_conflict(day, time2, course_name)):
                        
                        consecutive_pairs.append([(day, time1), (day, time2)])
        
        return consecutive_pairs
    
    def _select_optimal_slots(self, valid_slots: List[Tuple[str, str]], duration: int, course_name: str) -> List[Tuple[str, str]]:
        """Intelligently select optimal slots prioritizing consecutive times without conflicts."""
        
        # 🎯 PRIORITY 1: Find consecutive time slots on the same day
        consecutive_slots = self._find_consecutive_slots(valid_slots, duration)
        if consecutive_slots:
            print(f"   📅 Found consecutive slots: {consecutive_slots}")
            return consecutive_slots
        
        # 🎯 PRIORITY 2: Find slots that are close together (same or adjacent days)
        compact_slots = self._find_compact_slots(valid_slots, duration)
        if compact_slots:
            print(f"   📅 Found compact slots: {compact_slots}")
            return compact_slots
        
        # 🎯 PRIORITY 3: Fall back to intelligent distribution (original logic)
        print(f"   📅 Using distributed scheduling")
        return self._select_distributed_slots(valid_slots, duration)
    
    def _find_consecutive_slots(self, valid_slots: List[Tuple[str, str]], duration: int) -> List[Tuple[str, str]]:
        """Find consecutive time slots on the same day."""
        # Group by day
        days_slots = {}
        for day, time_slot in valid_slots:
            if day not in days_slots:
                days_slots[day] = []
            days_slots[day].append(time_slot)
        
        # Sort time slots and look for consecutive sequences
        for day, time_slots in days_slots.items():
            time_slots.sort(key=lambda x: self._get_time_index(x))
            
            # Look for consecutive sequences
            for i in range(len(time_slots) - duration + 1):
                consecutive_sequence = []
                for j in range(duration):
                    if i + j < len(time_slots):
                        current_time = time_slots[i + j]
                        expected_index = self._get_time_index(time_slots[i]) + j
                        actual_index = self._get_time_index(current_time)
                        
                        if actual_index == expected_index:
                            consecutive_sequence.append((day, current_time))
                        else:
                            break
                
                if len(consecutive_sequence) == duration:
                    return consecutive_sequence
        
        return []
    
    def _find_compact_slots(self, valid_slots: List[Tuple[str, str]], duration: int) -> List[Tuple[str, str]]:
        """Find slots that are close together (prioritizing same day, then adjacent days)."""
        # Group by day and sort by preference
        days_slots = {}
        for day, time_slot in valid_slots:
            if day not in days_slots:
                days_slots[day] = []
            days_slots[day].append((day, time_slot))
        
        # Sort each day's slots by time preference
        for day in days_slots:
            days_slots[day].sort(key=lambda x: self._get_time_preference(x[1]))
        
        selected = []
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        
        # Try to select from fewer days first
        for target_days in range(1, min(len(days_slots) + 1, duration + 1)):
            if len(selected) >= duration:
                break
                
            # Try different combinations of days
            available_days = [d for d in day_order if d in days_slots]
            for start_day_idx in range(len(available_days) - target_days + 1):
                selected = []
                days_to_use = available_days[start_day_idx:start_day_idx + target_days]
                
                # Distribute slots across these days
                slots_per_day = duration // len(days_to_use)
                remaining_slots = duration % len(days_to_use)
                
                for i, day in enumerate(days_to_use):
                    day_quota = slots_per_day + (1 if i < remaining_slots else 0)
                    available_in_day = min(day_quota, len(days_slots[day]))
                    selected.extend(days_slots[day][:available_in_day])
                
                if len(selected) >= duration:
                    return selected[:duration]
        
        return []
    
    def _select_distributed_slots(self, valid_slots: List[Tuple[str, str]], duration: int) -> List[Tuple[str, str]]:
        """Original distributed selection logic as fallback."""
        selected = []
        used_time_slots = set()
        
        # Group slots by day
        days_used = {}
        for day, time_slot in valid_slots:
            if day not in days_used:
                days_used[day] = []
            days_used[day].append((day, time_slot))
        
        # Sort available days
        available_days = sorted(list(days_used.keys()))
        
        # Select different time slots for distribution
        for day in available_days:
            if len(selected) >= duration:
                break
            
            day_slots = days_used[day]
            day_slots.sort(key=lambda x: self._get_time_preference(x[1]))
            
            # Try to find a time slot we haven't used yet
            for day_slot in day_slots:
                _, time_slot = day_slot
                if time_slot not in used_time_slots:
                    selected.append(day_slot)
                    used_time_slots.add(time_slot)
                    break
            else:
                # If all time slots are used, pick the best available
                if day_slots:
                    selected.append(day_slots[0])
                    used_time_slots.add(day_slots[0][1])
        
        # Fill remaining slots if needed
        if len(selected) < duration:
            remaining_slots = [slot for slot in valid_slots if slot not in selected]
            selected.extend(remaining_slots[:duration - len(selected)])
        
        return selected[:duration]
    
    def _get_time_index(self, time_slot: str) -> int:
        """Get the index of a time slot for consecutive checking."""
        time_order = [
            '09:00-10:00', '10:00-11:00', '11:00-12:00', '12:00-13:00',
            '13:00-14:00', '14:00-15:00', '15:00-16:00', '16:00-17:00', '17:00-18:00'
        ]
        return time_order.index(time_slot) if time_slot in time_order else 999
    
    def _get_time_preference(self, time_slot: str) -> int:
        """Get preference score for time slots (lower = better)."""
        # 🎯 INTELLIGENT PREFERENCES (9 AM to 6 PM)
        preferences = {
            '09:00-10:00': 3,  # Good morning time
            '10:00-11:00': 1,  # Prime time
            '11:00-12:00': 2,  # Good morning time
            '12:00-13:00': 6,  # Lunch time (less preferred)
            '13:00-14:00': 7,  # Post-lunch (less preferred)
            '14:00-15:00': 4,  # Good afternoon time
            '15:00-16:00': 5,  # OK afternoon time
            '16:00-17:00': 8,  # Late afternoon
            '17:00-18:00': 9   # Evening (least preferred)
        }
        return preferences.get(time_slot, 10)
    
    def solve_timetable(self) -> Dict:
        """Generate timetable using iterative per-session scheduling to satisfy weekly_count fairly."""
        if not self.training_data:
            if not self.load_training_data():
                return None

        print("🤖 Simple Solver initialized")
        print(f"\n🚀 Solving timetable for {self.training_data['metadata']['total_courses']} courses (iterative mode)...")
        print("=" * 60)

        # Reset state
        self.scheduled_slots.clear()
        self.faculty_schedule.clear()
        self.room_schedule.clear()
        self.course_schedule.clear()
        self.global_slot_usage.clear()
        self.day_load.clear()
        self.faculty_day_load.clear()
        self.expected_weekly.clear()
        self.actual_weekly.clear()
        self.failure_reasons.clear()

        courses_info = self.training_data['courses_info']

        # Build course state list
        course_states = []  # each: dict with remaining sessions/blocks
        for name, info in courses_info.items():
            avail = self.parse_availability_slots(info.get('available_slots', []))
            weekly = info.get('weekly_count', info.get('duration', 1))
            session_type = info.get('session_type', 'lecture')
            state = {
                'name': name,
                'faculty': info['faculty'],
                'room': info['room'],
                'session_type': session_type,
                'weekly_target': weekly,
                'remaining': weekly,   # lectures = sessions, labs = blocks
                'available_slots': avail,
                'density': weekly / max(1, len(avail))
            }
            # Expected weekly units: lectures count sessions; labs count block_hours * weekly
            if session_type == 'lab':
                self.expected_weekly[name] = weekly * self.default_lab_session_length
            else:
                self.expected_weekly[name] = weekly
            course_states.append(state)

        # Sort by descending density (harder first)
        course_states.sort(key=lambda c: (-c['density'], len(c['available_slots'])))

        round_idx = 0
        MAX_ROUNDS = 50  # safety
        while round_idx < MAX_ROUNDS:
            round_idx += 1
            progress = False
            # Iterate courses in priority order each round
            for state in course_states:
                if state['remaining'] <= 0:
                    continue
                if state['session_type'] == 'lab':
                    if self._schedule_one_lab_block(state):
                        state['remaining'] -= 1
                        progress = True
                else:
                    if self._schedule_one_lecture_session(state):
                        state['remaining'] -= 1
                        progress = True
            if not progress:
                break

        # Mark deficits
        for state in course_states:
            if state['remaining'] > 0 and state['name'] not in self.failure_reasons:
                scheduled = self.actual_weekly.get(state['name'], 0)
                expected = self.expected_weekly.get(state['name'], 0)
                self.failure_reasons[state['name']] = f'WEEKLY_DEFICIT_{scheduled}/{expected}'

        # Stats
        fully_satisfied = sum(1 for s in course_states if s['remaining'] == 0)
        unsatisfied = [s['name'] for s in course_states if s['remaining'] > 0]
        print(f"\n📊 Summary: {fully_satisfied} fully satisfied, {len(unsatisfied)} with deficits")
        if unsatisfied:
            print("   Deficit courses:")
            for u in unsatisfied:
                print(f"     - {u}: {self.failure_reasons.get(u)}")
            
            # Emergency relaxation attempt
            if len(unsatisfied) <= 3:  # Only if small number of deficits
                print(f"\n🚨 Attempting emergency relaxation for {len(unsatisfied)} courses...")
                self.MAX_FACULTY_SESSIONS_PER_DAY = 8  # Very high limit
                self.allow_parallel = True
                
                # Retry failed courses with relaxed constraints
                retry_rounds = 10
                for retry in range(retry_rounds):
                    progress = False
                    for state in course_states:
                        if state['remaining'] <= 0:
                            continue
                        if state['session_type'] == 'lab':
                            if self._schedule_one_lab_block(state):
                                state['remaining'] -= 1
                                progress = True
                        else:
                            if self._schedule_one_lecture_session(state):
                                state['remaining'] -= 1
                                progress = True
                    if not progress:
                        break
                
                # Update final stats
                fully_satisfied = sum(1 for s in course_states if s['remaining'] == 0)
                unsatisfied = [s['name'] for s in course_states if s['remaining'] > 0]
                print(f"   🔄 After relaxation: {fully_satisfied} satisfied, {len(unsatisfied)} still with deficits")

        timetable = dict(self.scheduled_slots)
        self._post_validate_weekly_counts()
        return timetable

    def _post_validate_weekly_counts(self):
        for course, expected in self.expected_weekly.items():
            actual = self.actual_weekly.get(course, 0)
            if actual < expected and course not in self.failure_reasons:
                self.failure_reasons[course] = f'WEEKLY_UNDERFILLED_{actual}/{expected}'
            elif actual > expected and course not in self.failure_reasons:
                self.failure_reasons[course] = f'WEEKLY_OVERFILLED_{actual}/{expected}'

    
    def export_solution(self, timetable: Dict, filename: str = './data/simple_timetable.json'):
        """Export timetable solution to JSON file."""
        try:
            # Convert to clean format
            clean_timetable = {}
            
            for day in self.days:
                clean_timetable[day] = {}
                for time_slot in self.time_slots:
                    if day in timetable and time_slot in timetable[day]:
                        clean_timetable[day][time_slot] = timetable[day][time_slot]
                    else:
                        clean_timetable[day][time_slot] = []
            
            with open(filename, 'w') as f:
                json.dump(clean_timetable, f, indent=2)
            
            print(f"✅ Solution exported to: {filename}")
            return True
            
        except Exception as e:
            print(f"❌ Error exporting solution: {str(e)}")
            return False
    
    def validate_timetable(self, timetable: Dict) -> Dict:
        """Validate timetable for conflicts."""
        conflicts = {
            'faculty_conflicts': [],
            'room_conflicts': [],
            'student_conflicts': [],
            'total_conflicts': 0
        }
        
        # Check each time slot for conflicts
        for day in timetable:
            for time_slot in timetable[day]:
                classes = timetable[day][time_slot]
                
                if len(classes) <= 1:
                    continue
                
                # Check faculty conflicts
                faculty_list = [cls['faculty'] for cls in classes]
                faculty_duplicates = set([f for f in faculty_list if faculty_list.count(f) > 1])
                
                for faculty in faculty_duplicates:
                    conflicts['faculty_conflicts'].append({
                        'day': day,
                        'time': time_slot,
                        'faculty': faculty,
                        'courses': [cls['course'] for cls in classes if cls['faculty'] == faculty]
                    })
                
                # Check room conflicts
                room_list = [cls['room'] for cls in classes]
                room_duplicates = set([r for r in room_list if room_list.count(r) > 1])
                
                for room in room_duplicates:
                    conflicts['room_conflicts'].append({
                        'day': day,
                        'time': time_slot,
                        'room': room,
                        'courses': [cls['course'] for cls in classes if cls['room'] == room]
                    })
                
                # 🎓 CHECK STUDENT CONFLICTS: Core courses that students take together
                course_list = [cls['course'] for cls in classes]
                for i, course1 in enumerate(course_list):
                    for course2 in course_list[i+1:]:
                        if self._courses_conflict(course1.lower(), course2.lower()):
                            conflicts['student_conflicts'].append({
                                'day': day,
                                'time': time_slot,
                                'courses': [course1, course2],
                                'reason': 'Core curriculum overlap'
                            })
        
        conflicts['total_conflicts'] = (len(conflicts['faculty_conflicts']) + 
                                      len(conflicts['room_conflicts']) + 
                                      len(conflicts['student_conflicts']))
        return conflicts
    
    def print_validation_report(self, timetable: Dict):
        """Print validation report."""
        conflicts = self.validate_timetable(timetable)
        
        if conflicts['total_conflicts'] == 0:
            print("\n✅ TIMETABLE VALIDATION: NO CONFLICTS FOUND!")
        else:
            print(f"\n⚠️ TIMETABLE VALIDATION: {conflicts['total_conflicts']} CONFLICTS FOUND")
            
            if conflicts['faculty_conflicts']:
                print("\n👨‍🏫 Faculty Conflicts:")
                for conflict in conflicts['faculty_conflicts']:
                    print(f"   - {conflict['faculty']} on {conflict['day']} {conflict['time']}")
                    print(f"     Courses: {', '.join(conflict['courses'])}")
            
            if conflicts['room_conflicts']:
                print("\n🏫 Room Conflicts:")
                for conflict in conflicts['room_conflicts']:
                    print(f"   - {conflict['room']} on {conflict['day']} {conflict['time']}")
                    print(f"     Courses: {', '.join(conflict['courses'])}")
            
            if conflicts['student_conflicts']:
                print("\n🎓 Student Conflicts (Courses students likely take together):")
                for conflict in conflicts['student_conflicts']:
                    print(f"   - {conflict['day']} {conflict['time']}: {', '.join(conflict['courses'])}")
                    print(f"     Reason: {conflict['reason']}")
        # Weekly count validation summary
        print("\n📊 Weekly Count Summary:")
        for course, expected in self.expected_weekly.items():
            actual = self.actual_weekly.get(course, 0)
            tag = 'OK' if actual == expected else 'MISMATCH'
            print(f"   {course}: {actual}/{expected} {tag}")
        if self.failure_reasons:
            print("\n⚠️  Failure reasons:")
            for c, r in self.failure_reasons.items():
                print(f"   {c}: {r}")

    def solve_timetable_from_data(self, training_data):
        """Solve timetable from provided training data (for API use)."""
        try:
            # Store the provided training data
            self.training_data = training_data
            
            # Solve using the standard method
            timetable = self.solve_timetable()
            
            return timetable
            
        except Exception as e:
            print(f"❌ Error solving timetable from data: {e}")
            return None

if __name__ == "__main__":
    solver = SimpleTimetableSolver()
    timetable = solver.solve_timetable()
    
    if timetable:
        solver.export_solution(timetable)
        solver.print_validation_report(timetable)
    else:
        print("❌ Failed to generate timetable")