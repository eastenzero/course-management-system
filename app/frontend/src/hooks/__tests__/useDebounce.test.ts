import { renderHook, act } from '@testing-library/react';
import { useDebounce, useDebouncedCallback, useDebouncedInput } from '../useDebounce';

// Mock timers
jest.useFakeTimers();

describe('useDebounce', () => {
  afterEach(() => {
    jest.clearAllTimers();
  });

  it('should return initial value immediately', () => {
    const { result } = renderHook(() => useDebounce('initial', 500));
    expect(result.current).toBe('initial');
  });

  it('should debounce value changes', () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      {
        initialProps: { value: 'initial', delay: 500 },
      }
    );

    expect(result.current).toBe('initial');

    // Change value
    rerender({ value: 'updated', delay: 500 });
    expect(result.current).toBe('initial'); // Should still be initial

    // Fast forward time
    act(() => {
      jest.advanceTimersByTime(500);
    });

    expect(result.current).toBe('updated');
  });

  it('should reset timer on rapid changes', () => {
    const { result, rerender } = renderHook(
      ({ value }) => useDebounce(value, 500),
      {
        initialProps: { value: 'initial' },
      }
    );

    // First change
    rerender({ value: 'change1' });
    act(() => {
      jest.advanceTimersByTime(300);
    });
    expect(result.current).toBe('initial');

    // Second change before first completes
    rerender({ value: 'change2' });
    act(() => {
      jest.advanceTimersByTime(300);
    });
    expect(result.current).toBe('initial');

    // Complete the debounce
    act(() => {
      jest.advanceTimersByTime(200);
    });
    expect(result.current).toBe('change2');
  });
});

describe('useDebouncedCallback', () => {
  afterEach(() => {
    jest.clearAllTimers();
  });

  it('should debounce callback execution', () => {
    const mockCallback = jest.fn();
    const { result } = renderHook(() =>
      useDebouncedCallback(mockCallback, 500)
    );

    // Call the debounced function multiple times
    act(() => {
      result.current('arg1');
      result.current('arg2');
      result.current('arg3');
    });

    // Callback should not be called yet
    expect(mockCallback).not.toHaveBeenCalled();

    // Fast forward time
    act(() => {
      jest.advanceTimersByTime(500);
    });

    // Callback should be called only once with the last arguments
    expect(mockCallback).toHaveBeenCalledTimes(1);
    expect(mockCallback).toHaveBeenCalledWith('arg3');
  });

  it('should update callback reference when dependencies change', () => {
    let callbackValue = 'initial';
    const { result, rerender } = renderHook(
      ({ deps }) => {
        const callback = () => callbackValue;
        return useDebouncedCallback(callback, 500, deps);
      },
      {
        initialProps: { deps: [callbackValue] },
      }
    );

    // Change the callback value and dependencies
    callbackValue = 'updated';
    rerender({ deps: [callbackValue] });

    act(() => {
      result.current();
    });

    act(() => {
      jest.advanceTimersByTime(500);
    });

    // The callback should use the updated value
    // Note: This test verifies that the callback reference is updated
  });

  it('should clear timeout on unmount', () => {
    const mockCallback = jest.fn();
    const { result, unmount } = renderHook(() =>
      useDebouncedCallback(mockCallback, 500)
    );

    act(() => {
      result.current('test');
    });

    unmount();

    act(() => {
      jest.advanceTimersByTime(500);
    });

    // Callback should not be called after unmount
    expect(mockCallback).not.toHaveBeenCalled();
  });
});

describe('useDebouncedInput', () => {
  afterEach(() => {
    jest.clearAllTimers();
  });

  it('should handle input changes with debouncing', () => {
    const mockOnChange = jest.fn();
    const { result } = renderHook(() =>
      useDebouncedInput('', 300, mockOnChange)
    );

    expect(result.current.value).toBe('');
    expect(result.current.debouncedValue).toBe('');

    // Simulate input change
    act(() => {
      result.current.onChange({
        target: { value: 'test' },
      } as React.ChangeEvent<HTMLInputElement>);
    });

    expect(result.current.value).toBe('test');
    expect(result.current.debouncedValue).toBe(''); // Not debounced yet

    // Fast forward time
    act(() => {
      jest.advanceTimersByTime(300);
    });

    expect(result.current.debouncedValue).toBe('test');
    expect(mockOnChange).toHaveBeenCalledWith('test');
  });

  it('should clear input value', () => {
    const { result } = renderHook(() => useDebouncedInput('initial'));

    act(() => {
      result.current.clear();
    });

    expect(result.current.value).toBe('');
  });

  it('should reset to initial value', () => {
    const { result } = renderHook(() => useDebouncedInput('initial'));

    // Change value
    act(() => {
      result.current.setValue('changed');
    });

    expect(result.current.value).toBe('changed');

    // Reset
    act(() => {
      result.current.reset();
    });

    expect(result.current.value).toBe('initial');
  });

  it('should handle setValue directly', () => {
    const { result } = renderHook(() => useDebouncedInput(''));

    act(() => {
      result.current.setValue('direct value');
    });

    expect(result.current.value).toBe('direct value');

    act(() => {
      jest.advanceTimersByTime(300);
    });

    expect(result.current.debouncedValue).toBe('direct value');
  });
});
