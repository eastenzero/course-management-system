import React from 'react';
import { DatePicker } from 'antd';
import type { RangePickerProps } from 'antd/es/date-picker';
import type { Dayjs } from 'dayjs';

const { RangePicker } = DatePicker;

export interface DateRangePickerProps extends RangePickerProps {
  onChange?: (dates: [Dayjs | null, Dayjs | null] | null, dateStrings: [string, string]) => void;
}

const DateRangePicker: React.FC<DateRangePickerProps> = (props) => {
  return <RangePicker {...props} />;
};

export default DateRangePicker;