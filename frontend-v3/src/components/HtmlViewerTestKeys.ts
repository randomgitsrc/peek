/**
 * HtmlViewer 测试注入 key
 *
 * 在测试中通过 provide(HTML_VIEWER_TEST_SIZE_KEY, bytes) 注入虚假内容大小，
 * 避免在 jsdom 里真实生成大字符串导致测试超时。
 *
 * 仅供测试使用，生产环境不会触发此注入点。
 */
export const HTML_VIEWER_TEST_SIZE_KEY = Symbol('htmlViewerTestContentSize')
