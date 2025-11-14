import { describe, it, expect, vi } from 'vitest';
import { renderHook } from '@testing-library/react';
import { useRef } from 'react';
import useOnClickOutside from './useOnClickOutside';

describe('useOnClickOutside', () => {
  it('should call handler when clicking outside element', () => {
    const handler = vi.fn();
    const ref = { current: document.createElement('div') };

    renderHook(() => useOnClickOutside(ref, handler));

    // Click outside
    const outsideElement = document.createElement('div');
    document.body.appendChild(outsideElement);
    outsideElement.dispatchEvent(new MouseEvent('mousedown', { bubbles: true }));

    expect(handler).toHaveBeenCalledTimes(1);

    document.body.removeChild(outsideElement);
  });

  it('should not call handler when clicking inside element', () => {
    const handler = vi.fn();
    const ref = { current: document.createElement('div') };

    renderHook(() => useOnClickOutside(ref, handler));

    // Click inside
    ref.current.dispatchEvent(new MouseEvent('mousedown', { bubbles: true }));

    expect(handler).not.toHaveBeenCalled();
  });

  it('should handle touch events', () => {
    const handler = vi.fn();
    const ref = { current: document.createElement('div') };

    renderHook(() => useOnClickOutside(ref, handler));

    // Touch outside
    const outsideElement = document.createElement('div');
    document.body.appendChild(outsideElement);
    outsideElement.dispatchEvent(new TouchEvent('touchstart', { bubbles: true }));

    expect(handler).toHaveBeenCalledTimes(1);

    document.body.removeChild(outsideElement);
  });

  it('should not call handler when touching inside element', () => {
    const handler = vi.fn();
    const ref = { current: document.createElement('div') };

    renderHook(() => useOnClickOutside(ref, handler));

    // Touch inside
    ref.current.dispatchEvent(new TouchEvent('touchstart', { bubbles: true }));

    expect(handler).not.toHaveBeenCalled();
  });

  it('should clean up event listeners on unmount', () => {
    const handler = vi.fn();
    const ref = { current: document.createElement('div') };
    const removeEventListenerSpy = vi.spyOn(document, 'removeEventListener');

    const { unmount } = renderHook(() => useOnClickOutside(ref, handler));
    unmount();

    expect(removeEventListenerSpy).toHaveBeenCalledWith('mousedown', expect.any(Function));
    expect(removeEventListenerSpy).toHaveBeenCalledWith('touchstart', expect.any(Function));
  });

  it('should not call handler with null refs', () => {
    const handler = vi.fn();
    const ref = { current: null };

    renderHook(() => useOnClickOutside(ref, handler));

    // Click anywhere - should not call handler because ref is null
    document.dispatchEvent(new MouseEvent('mousedown', { bubbles: true }));

    expect(handler).not.toHaveBeenCalled();
  });

  it('should handle clicking on child elements inside ref', () => {
    const handler = vi.fn();
    const parentDiv = document.createElement('div');
    const childDiv = document.createElement('div');
    parentDiv.appendChild(childDiv);
    const ref = { current: parentDiv };

    renderHook(() => useOnClickOutside(ref, handler));

    // Click on child
    childDiv.dispatchEvent(new MouseEvent('mousedown', { bubbles: true }));

    expect(handler).not.toHaveBeenCalled();
  });
});
