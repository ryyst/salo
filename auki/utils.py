def get_day_name(date):
    """Convert date to Finnish day abbreviation"""
    day_names = {0: "ma", 1: "ti", 2: "ke", 3: "to", 4: "pe", 5: "la", 6: "su"}
    return day_names[date.weekday()]


def group_consecutive_days(schedules):
    """Group consecutive days with same opening hours"""
    if not schedules:
        return []

    grouped = []
    current_group = [schedules[0]]

    for i in range(1, len(schedules)):
        current = schedules[i]
        previous = schedules[i - 1]

        # Check if current day has same time as previous and is consecutive
        if current["time_text"] == previous["time_text"] and is_consecutive_day(
            previous["date"], current["date"]
        ):
            current_group.append(current)
        else:
            # Different time or non-consecutive, finalize current group
            grouped.append(format_day_group(current_group))
            current_group = [current]

    # Add the last group
    grouped.append(format_day_group(current_group))

    return grouped


def is_consecutive_day(date1, date2):
    """Check if date2 is the day after date1"""
    return (date2 - date1).days == 1


def format_day_group(group):
    """Format a group of consecutive days with same hours"""
    if len(group) == 1:
        # Single day
        return f"{group[0]['day_name']} {group[0]['time_text']}"
    else:
        # Range of days
        first_day = group[0]["day_name"]
        last_day = group[-1]["day_name"]
        return f"{first_day}-{last_day} {group[0]['time_text']}"


def format_time(time_str):
    """Format time string, removing :00 minutes for on-the-hour times"""
    if time_str.endswith(":00"):
        return time_str[:-3]  # Remove ":00"
    return time_str
