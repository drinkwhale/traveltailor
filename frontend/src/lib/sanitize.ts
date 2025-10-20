/**
 * HTML Sanitization Utility - XSS 방어
 *
 * T032c: DOMPurify 설정 (XSS 방어)
 * - 사용자 입력 데이터 sanitization
 * - HTML 콘텐츠 정화
 * - XSS 공격 방어
 */

import DOMPurify from 'isomorphic-dompurify';

/**
 * Sanitization 옵션 타입
 */
interface SanitizeOptions {
  /**
   * 허용할 HTML 태그 (기본값: 안전한 태그만)
   */
  ALLOWED_TAGS?: string[];

  /**
   * 허용할 HTML 속성 (기본값: 안전한 속성만)
   */
  ALLOWED_ATTR?: string[];

  /**
   * 링크에 허용할 URI 스키마 (기본값: http, https, mailto만)
   */
  ALLOWED_URI_REGEXP?: RegExp;

  /**
   * 전체 HTML 문서를 반환할지 여부 (기본값: false, 조각만 반환)
   */
  RETURN_DOM?: boolean;

  /**
   * DOM Fragment를 반환할지 여부 (기본값: false)
   */
  RETURN_DOM_FRAGMENT?: boolean;

  /**
   * 안전하지 않은 요소를 제거할지 유지할지 (기본값: true, 제거)
   */
  SAFE_FOR_TEMPLATES?: boolean;
}

/**
 * 기본 sanitization 설정
 */
const DEFAULT_CONFIG: SanitizeOptions = {
  ALLOWED_TAGS: [
    'p',
    'br',
    'strong',
    'em',
    'u',
    'a',
    'ul',
    'ol',
    'li',
    'h1',
    'h2',
    'h3',
    'h4',
    'h5',
    'h6',
    'blockquote',
    'code',
    'pre',
    'span',
    'div',
  ],
  ALLOWED_ATTR: ['href', 'title', 'target', 'rel', 'class', 'id'],
  ALLOWED_URI_REGEXP: /^(?:(?:(?:f|ht)tps?|mailto|tel|callto|sms|cid|xmpp):|[^a-z]|[a-z+.\-]+(?:[^a-z+.\-:]|$))/i,
  SAFE_FOR_TEMPLATES: true,
};

/**
 * 엄격한 sanitization 설정 (텍스트만 허용)
 */
const STRICT_CONFIG: SanitizeOptions = {
  ALLOWED_TAGS: [],
  ALLOWED_ATTR: [],
  SAFE_FOR_TEMPLATES: true,
};

/**
 * 풍부한 텍스트 에디터용 sanitization 설정
 */
const RICH_TEXT_CONFIG: SanitizeOptions = {
  ALLOWED_TAGS: [
    'p',
    'br',
    'strong',
    'em',
    'u',
    's',
    'a',
    'ul',
    'ol',
    'li',
    'h1',
    'h2',
    'h3',
    'h4',
    'h5',
    'h6',
    'blockquote',
    'code',
    'pre',
    'hr',
    'table',
    'thead',
    'tbody',
    'tr',
    'th',
    'td',
    'img',
    'span',
    'div',
  ],
  ALLOWED_ATTR: [
    'href',
    'title',
    'target',
    'rel',
    'class',
    'id',
    'src',
    'alt',
    'width',
    'height',
    'style',
  ],
  ALLOWED_URI_REGEXP: /^(?:(?:(?:f|ht)tps?|mailto|tel|callto|sms|cid|xmpp|data):|[^a-z]|[a-z+.\-]+(?:[^a-z+.\-:]|$))/i,
  SAFE_FOR_TEMPLATES: true,
};

/**
 * HTML 문자열을 sanitize하여 XSS 공격 방어
 *
 * @param dirty - 정화할 HTML 문자열
 * @param options - Sanitization 옵션
 * @returns 정화된 HTML 문자열
 *
 * @example
 * ```typescript
 * const userInput = '<script>alert("XSS")</script><p>Safe content</p>';
 * const safe = sanitizeHtml(userInput);
 * // 결과: '<p>Safe content</p>'
 * ```
 */
export function sanitizeHtml(
  dirty: string,
  options: SanitizeOptions = DEFAULT_CONFIG
): string {
  if (!dirty || typeof dirty !== 'string') {
    return '';
  }

  try {
    const clean = DOMPurify.sanitize(dirty, options);
    return clean;
  } catch (error) {
    console.error('Error sanitizing HTML:', error);
    // 에러 발생 시 빈 문자열 반환 (안전 우선)
    return '';
  }
}

/**
 * 텍스트만 허용하는 엄격한 sanitization
 *
 * @param dirty - 정화할 문자열
 * @returns HTML 태그가 모두 제거된 텍스트
 *
 * @example
 * ```typescript
 * const userInput = '<b>Bold</b> text with <script>alert("XSS")</script>';
 * const safe = sanitizeText(userInput);
 * // 결과: 'Bold text with '
 * ```
 */
export function sanitizeText(dirty: string): string {
  return sanitizeHtml(dirty, STRICT_CONFIG);
}

/**
 * 풍부한 텍스트 콘텐츠를 sanitize (에디터용)
 *
 * @param dirty - 정화할 HTML 문자열
 * @returns 정화된 HTML 문자열 (더 많은 태그 허용)
 *
 * @example
 * ```typescript
 * const editorContent = '<h1>Title</h1><p>Content with <a href="https://example.com">link</a></p>';
 * const safe = sanitizeRichText(editorContent);
 * // 결과: 안전한 태그만 포함된 HTML
 * ```
 */
export function sanitizeRichText(dirty: string): string {
  return sanitizeHtml(dirty, RICH_TEXT_CONFIG);
}

/**
 * URL을 sanitize하여 안전한 URL만 허용
 *
 * @param url - 정화할 URL
 * @returns 안전한 URL 또는 빈 문자열
 *
 * @example
 * ```typescript
 * sanitizeUrl('https://example.com'); // 'https://example.com'
 * sanitizeUrl('javascript:alert("XSS")'); // ''
 * ```
 */
export function sanitizeUrl(url: string): string {
  if (!url || typeof url !== 'string') {
    return '';
  }

  // 허용된 프로토콜만 통과
  const allowedProtocols = ['http:', 'https:', 'mailto:', 'tel:'];

  try {
    const urlObj = new URL(url);

    if (!allowedProtocols.includes(urlObj.protocol)) {
      console.warn(`Blocked unsafe URL protocol: ${urlObj.protocol}`);
      return '';
    }

    return url;
  } catch {
    // 상대 URL이거나 잘못된 URL
    // 상대 URL은 허용 (서버 내부 링크)
    if (url.startsWith('/') || url.startsWith('./') || url.startsWith('../')) {
      return url;
    }

    // 그 외는 차단
    console.warn(`Blocked invalid URL: ${url}`);
    return '';
  }
}

/**
 * React에서 dangerouslySetInnerHTML 사용 시 안전하게 사용하기 위한 헬퍼
 *
 * @param html - 정화할 HTML 문자열
 * @returns { __html: string } 형태의 객체
 *
 * @example
 * ```tsx
 * <div dangerouslySetInnerHTML={createSafeMarkup(userContent)} />
 * ```
 */
export function createSafeMarkup(html: string): { __html: string } {
  return {
    __html: sanitizeHtml(html),
  };
}

/**
 * 여행 일정 설명 등 사용자 생성 콘텐츠를 sanitize
 *
 * @param content - 사용자 콘텐츠
 * @returns 정화된 콘텐츠
 */
export function sanitizeUserContent(content: string): string {
  // 여행 일정에 필요한 기본 포매팅만 허용
  const options: SanitizeOptions = {
    ALLOWED_TAGS: ['p', 'br', 'strong', 'em', 'ul', 'ol', 'li'],
    ALLOWED_ATTR: [],
    SAFE_FOR_TEMPLATES: true,
  };

  return sanitizeHtml(content, options);
}

/**
 * 검색 쿼리를 sanitize (특수 문자 이스케이프)
 *
 * @param query - 검색 쿼리
 * @returns 안전한 검색 쿼리
 */
export function sanitizeSearchQuery(query: string): string {
  if (!query || typeof query !== 'string') {
    return '';
  }

  // HTML 태그 제거
  const withoutTags = sanitizeText(query);

  // SQL 인젝션 방지를 위한 특수 문자 제거
  const safe = withoutTags.replace(/[;'"\\]/g, '');

  return safe.trim();
}

/**
 * 파일 이름을 sanitize (경로 탐색 공격 방지)
 *
 * @param filename - 파일 이름
 * @returns 안전한 파일 이름
 */
export function sanitizeFilename(filename: string): string {
  if (!filename || typeof filename !== 'string') {
    return '';
  }

  // 경로 구분자 및 위험한 문자 제거
  const safe = filename
    .replace(/[/\\]/g, '') // 경로 구분자 제거
    .replace(/\.\./g, '') // 상위 디렉토리 접근 방지
    .replace(/[<>:"|?*]/g, '') // 위험한 문자 제거
    .trim();

  return safe;
}

/**
 * DOMPurify 인스턴스 직접 접근 (고급 사용)
 */
export { DOMPurify };

/**
 * 미리 정의된 설정 export
 */
export const SanitizeConfigs = {
  DEFAULT: DEFAULT_CONFIG,
  STRICT: STRICT_CONFIG,
  RICH_TEXT: RICH_TEXT_CONFIG,
};
