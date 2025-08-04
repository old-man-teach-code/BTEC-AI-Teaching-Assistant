# Composables Documentation

This directory contains reusable Vue 3 composables for the BTEC AI Teaching Assistant dashboard.

## Structure

### `useAuth.js`
Handles user authentication and profile management.

**Exports:**
- `authStore` - Pinia auth store instance
- `username` - Computed property for user display name
- `loadUserProfile()` - Function to load user profile data

### `useCalendar.js`
Manages calendar functionality including events, navigation, and date calculations.

**Exports:**
- `events` - Array of calendar events
- `weekdays` - Array of weekday labels
- `currentMonthYear` - Computed property for current month/year display
- `calendarDays` - Computed property for calendar grid data
- `todaysEvents` - Computed property for today's events
- `formatEventTime()` - Function to format event time
- `previousMonth()` - Navigate to previous month
- `nextMonth()` - Navigate to next month
- `selectDate()` - Select a specific date

### `useStats.js`
Handles dashboard statistics and recent activities data.

**Exports:**
- `stats` - Reactive object with dashboard statistics
- `recentActivities` - Array of recent activities
- `documents` - Array of documents for charts
- `notificationCount` - Number of recent notifications
- `fetchStats()` - Function to load statistics from API
- `getTimeAgo()` - Helper function to format relative time

### `useEvents.js`
Manages calendar events data fetching.

**Exports:**
- `fetchCalendarEvents()` - Function to fetch and format calendar events

### `useColors.js`
Provides color mapping utilities for different data types.

**Exports:**
- `getTypeColor()` - Get color for file/activity type
- `getStatusColor()` - Get color for status
- `getPriorityColor()` - Get color for priority level

### `useUI.js`
Manages UI state and interactions.

**Exports:**
- `showDropdown` - Boolean for dropdown visibility
- `timeFilter` - Current time filter selection
- `toggleDropdown()` - Toggle dropdown visibility
- `setVisible()` - Set visibility state

## Usage

Import composables in your Vue component:

```javascript
import { useAuth, useCalendar, useStats } from '@/composables'

// Use in setup function
const { username } = useAuth()
const { events, formatEventTime } = useCalendar()
const { stats, fetchStats } = useStats()
```

Or import individually:

```javascript
import { useAuth } from '@/composables/useAuth'
```

## Benefits

1. **Separation of Concerns**: Each composable handles a specific domain
2. **Reusability**: Can be used across multiple components
3. **Testability**: Each composable can be tested independently
4. **Maintainability**: Easier to maintain and update specific functionality
5. **Type Safety**: Better TypeScript support when needed
