/** True on phones and tablets: a touch-first device with no fine pointer (mouse or trackpad),
 *  or a browser that says it's mobile. */
export const isMobile: boolean = (() => {
  // ?mobile forces it on (to try the touch UI on a desktop browser)
  if (new URLSearchParams(location.search).has('mobile')) return true;
  const nav = navigator as Navigator & { userAgentData?: { mobile?: boolean } };
  if (nav.userAgentData?.mobile) return true;
  if (/Android|iPhone|iPad|iPod|Mobile/i.test(navigator.userAgent)) return true;
  // iPadOS reports itself as a Mac; tell it apart by its touch points
  if (/Macintosh/.test(navigator.userAgent) && navigator.maxTouchPoints > 1) return true;
  return matchMedia('(pointer: coarse)').matches && !matchMedia('(any-pointer: fine)').matches;
})();
