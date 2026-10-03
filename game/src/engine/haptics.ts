/** A light tap of haptic feedback, for clicks on touch screens.
 *
 *  Android has `navigator.vibrate`. iOS Safari doesn't, but since iOS 18 toggling a native switch
 *  (`<input type="checkbox" switch>`) makes the system's haptic tick, and clicking its label does
 *  that from script, so an invisible one is kept on the page. Older iOS gets nothing. Either way
 *  it has to run soon after the tap (the browser's user activation), which a click handled in the
 *  next frame is. */
let iosSwitch: HTMLLabelElement | null = null;

export function haptic(): void {
  if (typeof navigator.vibrate === 'function') {
    navigator.vibrate(8);
    return;
  }
  if (!iosSwitch) {
    const label = document.createElement('label');
    label.setAttribute('aria-hidden', 'true');
    label.style.cssText = 'position:fixed;left:0;top:0;width:1px;height:1px;opacity:0;pointer-events:none;overflow:hidden';
    const input = document.createElement('input');
    input.type = 'checkbox';
    input.setAttribute('switch', '');
    input.tabIndex = -1;
    label.appendChild(input);
    document.body.appendChild(label);
    iosSwitch = label;
  }
  iosSwitch.click();
}
