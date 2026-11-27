/** What changed, newest first. Shown on the public "What's new" page. Write entries in plain words about what a person can now do. */
export interface ChangeEntry { date: string; title: string; items: string[] }

export const CHANGELOG: ChangeEntry[] = [
  {
    date: '2026-11-29', title: 'More calculators, a glossary and a self-check',
    items: [
      'Calculators: compare two loan offers, depreciation schedules, lease or buy, customer concentration, and "why does my number differ?", which tests the usual causes such as mid-year discounting and units. Break-even now has a chart.',
      'Calculator inputs are remembered in your browser, with one button to put them all back to the examples.',
      'A Glossary page with every term and where to see it used, and a Self-check page that runs textbook problems through the engine so you can see it agrees with a hand calculation.',
      'The site can be added to a phone or computer home screen. It still needs a connection to work.',
    ],
  },
  {
    date: '2026-11-28', title: 'Calculators, version comparison and an accountant handover pack',
    items: [
      'A Calculators page: loan with extra payments, savings goal, price from a target margin, true cost of a hire, break-even, working-capital what-if, GSTIN check and receivables ageing.',
      'On any saved model, "What changed" lists every value that differs from the previous version.',
      'Pin the pages you use most to the top of the menu, and print any page with a clean black-on-white layout.',
      'Settings can make a handover zip for your accountant: an Excel workbook of saved models, the full data export and your original files.',
    ],
  },
  {
    date: '2026-11-27', title: 'Industry readings, due dates, loans in the cash budget and easier reading',
    items: [
      'Ratios can be judged against an industry (software, retail, manufacturing, services, utilities), so a current ratio of 0.8 is read in context.',
      'Click the question mark on a key figure to see its working with your own numbers. Finance terms such as WACC and DSO explain themselves when you hover or focus them.',
      'Compare two uploads of the same kind of file to see which lines moved the most.',
      'A compliance calendar lists income-tax, tax-audit and GST dates, lets you tick off what is filed, and the Overview reminds you of anything due this week or overdue.',
      'The cash budget can charge interest on financing and repay it from spare cash. Forecasting has a trend-with-seasons method.',
      'The DCF has Undo and Redo. Settings has Text size, High contrast, an Excel export of your saved models and a list of your recent activity.',
      'A skip link lets keyboard users jump past the menu. If a page ever fails, you see a calm message and a short note is sent so it can be fixed.',
    ],
  },
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
