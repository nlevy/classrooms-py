# Client-Side Error Translation Examples

This directory contains example implementations for handling multilingual error messages from the Classroom Assignment Service API.

## Overview

The backend returns structured error responses with error codes and parameters:

```json
{
  "error": {
    "code": "STUDENT_NO_FRIENDS",
    "message": "Student 'Alice' has no friends listed",
    "params": {
      "studentName": "Alice"
    }
  }
}
```

Your client application translates these errors using the error code and parameters.

## Files

- **`i18n/errors-en.json`** - English error message templates
- **`i18n/errors-he.json`** - Hebrew error message templates
- **`error-translation-example.ts`** - TypeScript/JavaScript implementation
- **`react-example.tsx`** - React component examples

## Quick Start

### 1. Copy Translation Files

Copy the `i18n/` directory to your client project:

```bash
cp -r client_examples/i18n/ your-frontend-app/src/i18n/
```

### 2. Implement Translation Function

Use the provided `translateError` function or adapt it to your needs:

```typescript
import { translateError } from './error-translation-example';

// When handling API errors
const errorData = await response.json();
const translatedMessage = translateError(errorData, 'en'); // or 'he'
showErrorToUser(translatedMessage);
```

### 3. Handle API Requests

```typescript
try {
  const response = await fetch('/classrooms?classesNumber=3', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(students)
  });

  if (!response.ok) {
    const errorData = await response.json();
    const message = translateError(errorData, userLocale);
    displayError(message);
  }
} catch (error) {
  displayError('Network error');
}
```

## Integration Guides

### Vanilla JavaScript

```javascript
function translateError(errorResponse, locale = 'en') {
  const { code, params } = errorResponse.error;
  const template = translations[locale][code];

  let message = template;
  for (const [key, value] of Object.entries(params)) {
    message = message.replace(`{${key}}`, value);
  }

  return message;
}
```

### React

See `react-example.tsx` for complete examples including:
- Component-based error handling
- Custom hooks for API calls
- Context for locale management

### Vue.js

```javascript
// In your component
methods: {
  async assignClasses() {
    try {
      const response = await fetch(/* ... */);
      if (!response.ok) {
        const errorData = await response.json();
        this.errorMessage = this.translateError(errorData);
      }
    } catch (error) {
      this.errorMessage = this.$t('errors.network');
    }
  },

  translateError(errorData) {
    const template = this.$t(`errors.${errorData.error.code}`);
    let message = template;

    for (const [key, value] of Object.entries(errorData.error.params)) {
      message = message.replace(`{${key}}`, value);
    }

    return message;
  }
}
```

### Angular

```typescript
import { Injectable } from '@angular/core';
import { TranslateService } from '@ngx-translate/core';

@Injectable()
export class ErrorTranslationService {
  constructor(private translate: TranslateService) {}

  translateError(errorData: ErrorResponse): string {
    const { code, params } = errorData.error;
    return this.translate.instant(`errors.${code}`, params);
  }
}
```

## Adding New Languages

To add support for a new language (e.g., Spanish):

1. Create `i18n/errors-es.json`
2. Copy the structure from `errors-en.json`
3. Translate all messages
4. Update your translations object:

```typescript
const translations = {
  en: errorsEn,
  he: errorsHe,
  es: errorsEs,  // Add new language
};
```

## Error Code Reference

| Code | Description | Parameters |
|------|-------------|------------|
| `INVALID_CONTENT_TYPE` | Request not JSON | - |
| `MISSING_PARAMETER` | Required parameter missing | `parameter` |
| `INVALID_STUDENT_DATA` | Student data format error | `details` |
| `EMPTY_STUDENT_DATA` | No students provided | `count` |
| `MISSING_REQUIRED_FIELDS` | Required fields missing | `fields` (array) |
| `DUPLICATE_STUDENT_NAMES` | Duplicate names found | `duplicates` (array) |
| `STUDENT_NO_FRIENDS` | Student has no friends | `studentName` |
| `UNKNOWN_FRIEND` | Friend not in list | `studentName`, `friendName` |
| `ISOLATED_STUDENTS` | Students with no friendships | `students` (array) |
| `INVALID_CLASS_COUNT` | Invalid number of classes | `classCount` |
| `INVALID_STUDENT_COUNT` | Invalid number of students | `studentCount` |
| `TOO_MANY_CLASSES` | More classes than students | `classCount`, `studentCount` |
| `CLASS_SIZE_TOO_SMALL` | Resulting class too small | `minSize`, `classCount`, `studentCount` |
| `ASSIGNMENT_FAILED` | Assignment failed | - |
| `NO_SOLUTION_FOUND` | No valid solution | - |
| `OPTIMIZATION_TIMEOUT` | Solver timeout | - |
| `UNSUPPORTED_LANGUAGE` | Language not available | `language` |
| `TEMPLATE_NOT_AVAILABLE` | Template unavailable | - |
| `INTERNAL_SERVER_ERROR` | Unexpected error | `details` |

## Best Practices

### 1. Fallback Strategy

Always provide fallback for missing translations:

```typescript
const template = translations[locale]?.[code] ||
                 translations['en']?.[code] ||
                 errorResponse.error.message;
```

### 2. Array Parameters

Format arrays nicely for display:

```typescript
const displayValue = Array.isArray(value)
  ? value.join(', ')
  : String(value);
```

### 3. Error Logging

Log the original error for debugging:

```typescript
console.error('API Error:', {
  code: errorData.error.code,
  message: errorData.error.message,
  params: errorData.error.params
});
```

### 4. User-Friendly Messages

The translation files use user-friendly language. Feel free to customize messages for your specific use case.

## Testing

Test your error handling with different error codes:

```typescript
// Simulate different errors
const testErrors = [
  {
    error: {
      code: 'STUDENT_NO_FRIENDS',
      params: { studentName: 'Alice' },
      message: 'Debug message'
    }
  },
  {
    error: {
      code: 'TOO_MANY_CLASSES',
      params: { classCount: 10, studentCount: 5 },
      message: 'Debug message'
    }
  }
];

testErrors.forEach(error => {
  console.log('EN:', translateError(error, 'en'));
  console.log('HE:', translateError(error, 'he'));
});
```

## Support

For questions or issues:
- Check the API documentation
- Review the error code reference above
- Ensure your translation files match the latest error codes
