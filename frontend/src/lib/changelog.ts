/** What changed, newest first. Shown on the public "What's new" page. Write entries in plain words about what a person can now do. */
export interface ChangeEntry { date: string; title: string; items: string[] }

export const CHANGELOG: ChangeEntry[] = [
  {
    date: '2026-11-26', title: 'Plain-English readings, messier files, and a front door',
    items: [
      'Every ratio now says what it means, what is typical, what could mislead and what to look at next, with an overall reading and a DuPont breakdown of return on equity.',
      'DCF, forecasts, project appraisal, variance, red flags, scenarios, the cash budget, sensitivity and peer comparison open with a short reading of the result and a link to the sensible next step.',
      'The DCF checks your assumptions (terminal growth, capital spending against depreciation, tax rate, margin gains, a growth cliff) and offers four template starting points.',
      'Uploads: decimal-comma numbers, year-style headers, Windows-encoded text, numbers inside sentences and logs, Markdown and HTML tables, RTF, JSON, JSON Lines, YAML, TOML and XML are read, and unusual things (a unit slip, a total that does not add up) are flagged before any analysis.',
      'Numbers read from sentences are placed by the period named beside them and feed the ratio and statement engines. Drop a file anywhere in the app to analyse it.',
      'Visitors can try a working calculator without an account. Signed-in users get Ctrl+K search (pages, files, saved models, actions), keyboard shortcuts (press ?), a "pick up where you left off" card and a sample company.',
      'Type 45k, 3.5L, 1.2cr, 2m or 12% in number boxes.',
      'Password reset by email, and sign-in, sign-up and reset limits that survive restarts.',
      'Settings: choose a moving, still or no 3D background.',
    ],
  },
  {
    date: '2026-10-26', title: 'ITR from your documents and tax audit (3CB / 3CD)',
    items: ['Upload Form 16, 26AS, AIS and capital-gains statements to find the right ITR form, with the source of every answer.', 'Tax audit: section 44AB applicability, Form 3CA or 3CB, and a Form 3CD draft filled from your accounts.'],
  },
];
