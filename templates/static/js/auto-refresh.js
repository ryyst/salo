/**
 * Auto-refresh functionality for apps with periodic data updates
 * Schedules page refreshes at specific minutes of each hour
 */
function scheduleAutoRefresh(targetMinutes) {
  if (!Array.isArray(targetMinutes) || targetMinutes.length === 0) {
    return;
  }

  function scheduleNext() {
    const now = new Date();
    const currentMinute = now.getMinutes();

    // Find next target minute in current hour
    let nextTarget = targetMinutes.find((min) => min > currentMinute);

    // If no target found in current hour, use first target of next hour
    if (!nextTarget) {
      nextTarget = targetMinutes[0] + 60;
    }

    // Calculate milliseconds until next refresh
    const minutesUntilRefresh = nextTarget - currentMinute;
    const msUntilRefresh =
      (minutesUntilRefresh * 60 - now.getSeconds()) * 1000 -
      now.getMilliseconds();

    // Log next refresh time for debugging
    const nextRefreshTime = new Date(now.getTime() + msUntilRefresh);
    console.log(
      `Auto-refresh scheduled for ${nextRefreshTime.toLocaleTimeString()}`,
    );

    setTimeout(() => {
      console.log("Auto-refreshing page...");
      window.location.reload();
    }, msUntilRefresh);
  }

  // Start the refresh cycle
  scheduleNext();
}

// Export for use in templates
window.scheduleAutoRefresh = scheduleAutoRefresh;
