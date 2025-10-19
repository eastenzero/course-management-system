export const normalizeSemester = (input: string): string => {
  if (!input) return input;
  const s = input.trim().replace(/\s+/g, '');
  const simple = s.match(/^(\d{4})-(1|2)$/);
  if (simple) {
    const year = +simple[1];
    return simple[2] === '1'
      ? `${year}-${year + 1}-1`
      : `${year - 1}-${year}-2`;
  }
  const zh = s.match(/(\d{4}).*(春|秋)/);
  if (zh) {
    const year = +zh[1];
    return zh[2] === '春'
      ? `${year - 1}-${year}-2`
      : `${year}-${year + 1}-1`;
  }
  return s;
};

export const semesterToAcademicYear = (input: string): string => {
  const s = normalizeSemester(input);
  const m = s.match(/^(\d{4})-(\d{4})-(1|2)$/);
  if (m) return `${m[1]}-${m[2]}`;
  return s;
};
