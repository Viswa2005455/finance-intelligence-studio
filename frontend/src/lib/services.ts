/**
 * The public catalogue of freelance services shown at /services.
 * Each service has its own page at /services/<slug>. Prices are starting prices in rupees.
 */

export const CONTACT = {
  name: 'Viswa Kumar',
  email: 'fabulousviswa2005@gmail.com',
  whatsapp: '916385364311', // country code + number, digits only (used in wa.me links)
  whatsappDisplay: '+91 63853 64311',
  store: 'https://fabulousviswa.gumroad.com',
};

export type CategoryId = 'excel' | 'powerbi' | 'web' | 'automation' | 'research';

export const CATEGORIES: { id: CategoryId; label: string; blurb: string }[] = [
  { id: 'excel', label: 'Excel & financial reporting', blurb: 'Dashboards, trackers and models built in Excel with live formulas.' },
  { id: 'powerbi', label: 'Power BI & analytics', blurb: 'Interactive dashboards and monthly management reports.' },
  { id: 'web', label: 'Websites', blurb: 'Responsive websites and landing pages for small businesses.' },
  { id: 'automation', label: 'Automation & trackers', blurb: 'Google Sheets and workflow automation that removes repetitive work.' },
  { id: 'research', label: 'Research, decks & documents', blurb: 'Financial analysis, research reports and presentations.' },
];

/** Every package includes the instant ready-made kit. Basic is the kit only (days 0, no custom work);
 *  Standard and Premium add custom work delivered by email within `days`. */
export interface Tier { name: 'Basic' | 'Standard' | 'Premium'; price: number; days: number; revisions: number; includes: string; custom: boolean }

export interface Service {
  id: number;
  slug: string;
  category: CategoryId;
  title: string;
  promise: string;
  forWho: string;
  tiers: Tier[];
  youSend: string;
  sample?: { label: string; url: string };
}

type Row = [
  CategoryId, string, string, string,
  [number, number, number], [number, number, number],
  string, string, string, string,
  { label: string; url: string }?,
];

const slugify = (s: string) => s.toLowerCase().replace(/&/g, 'and').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');

// [category, title, promise, for whom, prices, delivery days, basic, standard, premium, what you send, sample?]
const ROWS: Row[] = [
  // ---------------------------------------------------------------- Excel & financial reporting
  ['excel', 'Custom Excel dashboard', 'A clean, one-screen Excel dashboard of your key numbers with charts that update when you add data.', 'Small businesses, shops and managers who track numbers in Excel',
    [99, 249, 349], [3, 4, 6], 'Up to 4 KPIs and 2 charts on one sheet', 'Up to 8 KPIs, 4 charts and a month selector', 'Up to 12 KPIs, 6 charts, month selector and a printable summary', 'Your Excel data or a sample of it, and the numbers you want to see'],
  ['excel', 'Personal budget tracker (customised)', 'A personal budget tracker set up with your own income and spending categories and monthly budgets.', 'Students, young professionals and families',
    [299, 399, 499], [1, 2, 3], 'Your categories and budgets added to the tracker', 'Plus savings goals and a yearly summary', 'Plus debt/EMI tracker and a 30-minute walkthrough call', 'Your categories and monthly budget amounts',
    { label: 'See the ready-made template', url: 'https://fabulousviswa.gumroad.com/l/poizn' }],
  ['excel', 'Small business profit & loss dashboard (customised)', 'A monthly profit and loss dashboard for your business: revenue, gross profit, net profit and margins.', 'Shops, restaurants, traders and home businesses',
    [399, 449, 499], [2, 3, 5], 'Your revenue and cost categories added', 'Plus your past months entered and a trend chart', 'Plus product-wise profit and a printable monthly report', 'Your sales and expense records (Excel, Tally export or notebook photos)',
    { label: 'See the ready-made template', url: 'https://fabulousviswa.gumroad.com/l/egzic' }],
  ['excel', 'Budget vs actual variance report', 'A report that compares your budget with actual results and highlights where and why you overspent.', 'Business owners, finance teams and project managers',
    [99, 249, 349], [2, 3, 5], 'One period, up to 15 line items', 'Monthly report for a year with variance flags', 'Plus department-wise views and written commentary', 'Your budget and your actual figures'],
  ['excel', 'Cash flow forecast model (12 months)', 'A 12-month cash flow forecast so you can see when cash will run short before it happens.', 'Startups, small businesses and freelancers',
    [99, 299, 399], [3, 4, 6], 'Monthly cash in and out for 12 months', 'Plus three scenarios (base, best, worst)', 'Plus weekly view for the first 3 months and a summary dashboard', 'Opening cash balance, expected income and regular expenses'],
  ['excel', 'Sales tracking dashboard', 'A sales dashboard showing revenue by month, product and salesperson.', 'Shops, distributors and sales teams',
    [99, 249, 349], [2, 3, 5], 'Monthly sales total and top products', 'Plus salesperson and region views', 'Plus targets vs actual and growth rates', 'Your sales records in any format'],
  ['excel', 'Inventory / stock tracker', 'An Excel stock tracker with stock in, stock out, current balance and low-stock alerts.', 'Retail shops, pharmacies and small warehouses',
    [99, 249, 349], [2, 3, 4], 'Up to 100 items with balance and alerts', 'Up to 500 items plus supplier list', 'Plus stock value and fast/slow-moving item report', 'Your item list and current stock'],
  ['excel', 'Expense tracker for shops', 'A simple daily expense tracker for your shop with monthly totals by category.', 'Shop owners and small offices',
    [99, 249, 349], [1, 2, 3], 'Daily entry sheet and monthly totals', 'Plus category chart and yearly summary', 'Plus cash vs UPI vs card split and printable report', 'Your expense categories'],
  ['excel', 'GST invoice and register template', 'A GST invoice template that fills itself and keeps a sales register for you.', 'Small GST-registered businesses',
    [99, 249, 349], [1, 2, 3], 'Invoice template with your details and tax calculation', 'Plus automatic sales register', 'Plus monthly GST summary sheet', 'Your business details and GST rates you use'],
  ['excel', 'Financial ratio analysis workbook', 'A workbook that calculates profitability, liquidity, solvency and efficiency ratios from financial statements.', 'Students, analysts and small business owners',
    [99, 249, 349], [2, 3, 4], 'Ratios for one year', 'Ratios for up to 5 years with trends', 'Plus peer comparison and written interpretation', 'Balance sheet and profit & loss statements'],
  ['excel', 'Excel data cleaning and formatting', 'Your messy Excel file cleaned: duplicates removed, columns fixed, formats made consistent.', 'Anyone with messy spreadsheets',
    [99, 199, 299], [1, 1, 2], 'Up to 1,000 rows', 'Up to 10,000 rows', 'Up to 50,000 rows plus a summary of changes', 'Your Excel or CSV file'],
  ['excel', 'PivotTable reports from your data', 'Raw data turned into clear PivotTable summaries and charts you can refresh yourself.', 'Managers and teams with large data exports',
    [99, 199, 299], [1, 2, 3], 'Up to 3 PivotTable summaries', 'Up to 6 summaries with charts', 'Plus slicers and a one-page report', 'Your data file and the questions you want answered'],

  // ---------------------------------------------------------------- Power BI & analytics
  ['powerbi', 'Power BI sales dashboard', 'An interactive Power BI sales dashboard with filters for month, product and region.', 'Businesses that want interactive reporting',
    [99, 299, 399], [3, 5, 7], 'One page with key sales KPIs', 'Two pages with filters and drill-down', 'Three pages, custom measures and a usage guide', 'Your sales data (Excel or CSV)'],
  ['powerbi', 'Power BI financial KPI dashboard', 'A Power BI dashboard of revenue, profit, margins and expenses for management review.', 'Business owners and finance teams',
    [99, 299, 399], [3, 5, 7], 'One page of financial KPIs', 'Two pages with monthly trends', 'Three pages with budget vs actual and explanations', 'Your financial data'],
  ['powerbi', 'Excel to Power BI conversion', 'Your existing Excel reports rebuilt as an interactive Power BI dashboard.', 'Teams that outgrew Excel reports',
    [99, 299, 399], [3, 5, 7], 'One Excel report converted', 'Up to three reports converted', 'Up to five reports with a shared data model', 'Your current Excel reports'],
  ['powerbi', 'Monthly management report (MIS)', 'A monthly MIS report with the numbers your management needs, in one consistent format.', 'Small and medium businesses',
    [99, 249, 349], [3, 4, 6], 'Up to 10 key figures', 'Up to 20 figures with charts', 'Plus written commentary and comparison with last month', 'Your monthly data and the figures management reviews'],
  ['powerbi', 'Coaching centre fee and admission dashboard', 'A dashboard tracking enquiries, admissions, fees collected and fees pending.', 'Coaching centres, tuition centres and institutes',
    [99, 299, 399], [3, 5, 7], 'Admissions and fee collection summary', 'Plus pending fees list and batch-wise view', 'Plus enquiry-to-admission conversion tracking', 'Your student and fee records'],
  ['powerbi', 'Restaurant revenue and expense dashboard', 'A dashboard of daily sales, food cost and expenses so you know your real profit.', 'Restaurants, cafes and cloud kitchens',
    [99, 249, 349], [3, 4, 6], 'Monthly sales and expenses', 'Plus daily trend and best-selling items', 'Plus food cost percentage and profit per day', 'Your sales and purchase records'],
  ['powerbi', 'Retail shop profit dashboard', 'A dashboard showing your shop\'s sales, margins and best and worst products.', 'Retail and grocery shops',
    [99, 249, 349], [3, 4, 6], 'Monthly sales and profit', 'Plus product-wise margins', 'Plus slow-moving stock and seasonal trends', 'Your sales and purchase data'],
  ['powerbi', 'Budget planning model for startups', 'A yearly budget model for a startup: hiring, expenses, revenue and runway.', 'Early-stage startups and founders',
    [99, 299, 399], [3, 5, 7], '12-month budget', 'Plus hiring plan and runway calculation', 'Plus 3 scenarios and an investor-ready summary', 'Your plans, costs and revenue assumptions'],
  ['powerbi', 'Break-even and pricing analysis', 'A model showing how many units you must sell to break even and how price changes affect profit.', 'New businesses and product sellers',
    [99, 249, 349], [2, 3, 4], 'Break-even for one product', 'Up to five products with a pricing table', 'Plus what-if analysis and recommendations', 'Your costs and current prices'],
  ['powerbi', 'Monthly dashboard update (recurring)', 'I update your existing dashboard with new data every month, so it is always current.', 'Clients who already have a dashboard',
    [99, 199, 299], [2, 2, 2], 'Monthly data refresh (price per month)', 'Plus a short summary of changes', 'Plus a 30-minute monthly review call', 'Your new data each month'],

  // ---------------------------------------------------------------- Websites
  ['web', 'One-page landing page', 'A fast, mobile-friendly one-page website for your business, product or event.', 'Small businesses, events and new products',
    [99, 249, 349], [3, 4, 5], 'One page with up to 4 sections', 'Up to 7 sections and a contact form', 'Plus WhatsApp button, map and basic SEO', 'Your text, logo and photos'],
  ['web', 'Small business website (up to 5 pages)', 'A professional website of up to 5 pages that works on phones and computers.', 'Shops, clinics, consultants and service businesses',
    [149, 399, 499], [5, 7, 10], 'Up to 3 pages', 'Up to 5 pages with contact form', 'Up to 5 pages, gallery, map and basic SEO', 'Your business details, text, logo and photos'],
  ['web', 'Personal portfolio website', 'A personal portfolio website to show your work, resume and contact details.', 'Students, freelancers and job seekers',
    [99, 299, 399], [3, 4, 5], 'One-page portfolio', 'Up to 3 pages with project showcase', 'Plus blog section and custom domain setup help', 'Your resume, projects and photo'],
  ['web', 'Coaching centre website with enquiry form', 'A website for your coaching centre with courses, batches and an enquiry form that reaches you.', 'Coaching centres and training institutes',
    [149, 399, 499], [5, 7, 10], 'Up to 3 pages with enquiry form', 'Up to 5 pages with course list and gallery', 'Plus results page, testimonials and basic SEO', 'Your course details, batches, logo and photos'],
  ['web', 'Restaurant website with menu', 'A restaurant website with your menu, timings, location and WhatsApp ordering button.', 'Restaurants, cafes and bakeries',
    [149, 349, 449], [4, 5, 7], 'One page with menu and location', 'Up to 4 pages with photo gallery', 'Plus table booking enquiry form and basic SEO', 'Your menu, photos, timings and address'],
  ['web', 'Website redesign / refresh', 'Your old website redesigned to look modern and work properly on mobile phones.', 'Businesses with an outdated website',
    [99, 299, 399], [4, 6, 8], 'Redesign of up to 2 pages', 'Up to 5 pages', 'Up to 8 pages plus speed improvements', 'Access to your current website'],
  ['web', 'Mobile responsiveness fix', 'Your website fixed so it displays correctly on phones and tablets.', 'Website owners whose site breaks on mobile',
    [99, 249, 349], [1, 2, 3], 'Up to 2 pages fixed', 'Up to 5 pages fixed', 'Up to 10 pages fixed and tested on several devices', 'Access to your website code or builder'],
  ['web', 'Google Business Profile setup', 'Your Google Business Profile set up so customers can find you on Google Maps and Search.', 'Local shops and service businesses',
    [99, 199, 299], [1, 2, 2], 'Profile created with basic details', 'Plus photos, services and business hours', 'Plus posts and a guide to collecting reviews', 'Your business details and photos'],
  ['web', 'Website maintenance (monthly)', 'Ongoing website updates, fixes and backups so you don\'t have to worry about it.', 'Businesses with an existing website',
    [99, 199, 299], [30, 30, 30], 'Up to 2 small updates per month (price per month)', 'Up to 5 updates and monthly check', 'Up to 10 updates, backups and a monthly report', 'Access to your website'],
  ['web', 'Basic on-page SEO setup', 'Page titles, descriptions, headings and images set up so search engines understand your site.', 'Small business websites',
    [99, 249, 349], [2, 3, 5], 'Up to 3 pages', 'Up to 8 pages plus sitemap', 'Up to 15 pages plus Search Console setup', 'Access to your website and your main keywords'],

  // ---------------------------------------------------------------- Automation & trackers
  ['automation', 'Automated weekly sales report', 'A sales report that builds itself every week from your data, so you stop copying numbers by hand.', 'Businesses that prepare the same report every week',
    [99, 299, 399], [4, 6, 8], 'One report from one data source', 'Plus automatic email to you', 'Up to two sources plus charts in the email', 'Your current report and where the data comes from'],
  ['automation', 'Google Sheets lead / enquiry tracker', 'A shared Google Sheet to track every enquiry, follow-up date and status.', 'Sales teams, coaching centres and agencies',
    [99, 249, 349], [1, 2, 3], 'Tracker with status and follow-up dates', 'Plus follow-up reminder highlighting', 'Plus dashboard of conversions by source', 'How you get leads today'],
  ['automation', 'Google Form to Sheet to email automation', 'Form responses saved to a Sheet automatically, with an email to you for each new response.', 'Anyone collecting enquiries, orders or registrations',
    [99, 249, 349], [2, 3, 5], 'Form linked to a Sheet', 'Plus email notification to you', 'Plus confirmation email to the person who filled it', 'The questions your form should ask'],
  ['automation', 'Invoice generator in Sheets/Excel', 'An invoice generator that numbers invoices, calculates totals and keeps a record of each one.', 'Freelancers and small businesses',
    [99, 249, 349], [1, 2, 3], 'Invoice template with automatic totals', 'Plus invoice register and numbering', 'Plus payment status tracking and monthly summary', 'Your business details and a sample invoice'],
  ['automation', 'Student attendance and fee tracker', 'A tracker for daily attendance and monthly fees, with a list of pending payments.', 'Tuition centres, schools and coaching centres',
    [99, 249, 349], [2, 3, 4], 'Attendance and fee sheets for one batch', 'Up to 5 batches with pending fee list', 'Plus monthly reports per student', 'Student list and fee structure'],
  ['automation', 'Appointment / booking tracker', 'A booking tracker that shows your appointments by day and prevents double bookings.', 'Clinics, salons and consultants',
    [99, 249, 349], [2, 3, 4], 'Booking sheet with daily view', 'Plus double-booking warning', 'Plus Google Form booking and summary report', 'Your working hours and services'],
  ['automation', 'n8n / Make workflow setup (simple)', 'A simple automation that connects your apps, for example new form entry to Sheet to email.', 'Businesses wanting to remove repetitive tasks',
    [149, 349, 449], [4, 6, 10], 'One workflow with up to 3 steps', 'One workflow with up to 6 steps and error alerts', 'Up to 3 workflows with documentation', 'The task you want automated and access to the apps involved'],
  ['automation', 'Excel automation with formulas (no macros)', 'Repetitive Excel work automated with formulas and lookups, without macros.', 'Anyone repeating the same Excel steps',
    [99, 249, 349], [1, 2, 3], 'One repetitive task automated', 'Up to three tasks', 'Up to five tasks plus a how-to guide', 'Your file and a description of the steps you repeat'],
  ['automation', 'Data entry system with dropdowns and validation', 'An Excel or Sheets entry form with dropdowns and checks so data is entered correctly every time.', 'Offices and teams entering data by hand',
    [99, 199, 299], [1, 2, 3], 'One entry sheet with dropdowns', 'Plus validation rules and error highlighting', 'Plus summary sheet and protected formulas', 'The fields you need to capture'],

  // ---------------------------------------------------------------- Research, decks & documents
  ['research', 'Company financial analysis report', 'A clear financial analysis of a listed company from its public reports: growth, profitability and risks.', 'Students, investors and job applicants',
    [99, 249, 349], [2, 4, 6], '3-year summary and key ratios', '5-year analysis with charts', 'Plus peer comparison and written conclusion', 'The company name'],
  ['research', 'Industry / market research report', 'A structured report on an industry: size, key players, trends and opportunities, with sources.', 'Students, startups and business owners',
    [99, 249, 349], [3, 4, 6], '5-page summary', '10-page report with charts', '15-page report with competitor profiles', 'The industry and what you need it for'],
  ['research', 'Competitor analysis', 'A side-by-side comparison of your competitors\' products, prices and strengths.', 'Small businesses and startups',
    [99, 249, 349], [2, 3, 5], 'Up to 3 competitors', 'Up to 6 competitors with comparison table', 'Up to 10 competitors with recommendations', 'Your business and your main competitors'],
  ['research', 'Business plan financial projections', 'Financial projections for your business plan: revenue, costs, profit and cash for 3 to 5 years.', 'Startups and loan applicants',
    [99, 299, 399], [3, 5, 7], '3-year projections', '5-year projections with assumptions sheet', 'Plus break-even, ratios and scenario analysis', 'Your business idea, prices and expected costs'],
  ['research', 'Pitch deck financial slides', 'The financial slides for your pitch deck: market size, revenue model, projections and funding ask.', 'Founders preparing to pitch',
    [99, 249, 349], [2, 4, 5], 'Up to 3 slides', 'Up to 6 slides with charts', 'Up to 10 slides plus speaker notes', 'Your existing deck or business details'],
  ['research', 'Professional PowerPoint presentation', 'A clean, professional presentation designed from your content.', 'Students, professionals and businesses',
    [99, 249, 349], [2, 3, 5], 'Up to 10 slides', 'Up to 20 slides with charts and icons', 'Up to 30 slides with custom design', 'Your content or notes'],
  ['research', 'LinkedIn profile optimisation', 'Your LinkedIn headline, about section and experience rewritten to attract recruiters and clients.', 'Students, job seekers and freelancers',
    [99, 199, 299], [1, 2, 3], 'Headline and about section', 'Plus experience section and skills', 'Plus banner image and a content plan', 'Your current profile link or resume'],
  ['research', 'Resume / CV for finance roles', 'A clear, ATS-friendly resume tailored for finance, accounting and analyst roles.', 'Finance and commerce students and job seekers',
    [1, 199, 299], [1, 2, 3], 'Resume rewritten in a clean format', 'Plus cover letter', 'Plus LinkedIn summary and two tailored versions', 'Your current resume and target role'],
  ['research', 'Social media content calendar (1 month)', 'A month of social media post ideas, captions and a posting schedule.', 'Small businesses and personal brands',
    [99, 249, 349], [2, 3, 5], '12 post ideas with captions', '20 posts with captions and hashtags', '30 posts plus simple designs in Canva', 'Your business, audience and goals'],
];

export const SERVICES: Service[] = ROWS.map((r, i) => {
  const [category, title, promise, forWho, prices, days, basic, standard, premium, youSend, sample] = r;
  const names = ['Basic', 'Standard', 'Premium'] as const;
  // Some rows describe a tier as "Plus ..." (on top of the one before). Spell the full scope out for each tier.
  const scope: string[] = [];
  [basic, standard, premium].forEach((txt, t) => {
    scope[t] = /^plus\s/i.test(txt) ? `${scope[t - 1]}, plus ${txt.replace(/^plus\s+/i, '')}` : txt;
  });
  const includes = scope;
  return {
    id: i + 1,
    slug: slugify(title),
    category, title, promise, forWho, youSend, sample,
    tiers: names.map((name, t) => t === 0
      ? { name, price: prices[t], days: 0, revisions: 0, custom: false, includes: 'The ready-made kit, delivered the moment you pay. Fill it in yourself with the how-to guide.' }
      : { name, price: prices[t], days: days[t], revisions: t + 1, custom: true, includes: `The instant ready-made kit, plus custom work for you: ${includes[t].charAt(0).toLowerCase()}${includes[t].slice(1)}` }),
  };
});

export const formatINR = (n: number) => '₹' + n.toLocaleString('en-IN');

export function enquiryText(s: Service, tier?: Tier) {
  return `Hi ${CONTACT.name}, I'm interested in your service "${s.title}"${tier ? ` (${tier.name} package, ${formatINR(tier.price)})` : ''}. `;
}
export const whatsappLink = (s: Service, tier?: Tier) =>
  `https://wa.me/${CONTACT.whatsapp}?text=${encodeURIComponent(enquiryText(s, tier))}`;
export const emailLink = (s: Service, tier?: Tier) =>
  `mailto:${CONTACT.email}?subject=${encodeURIComponent(`Service enquiry: ${s.title}`)}&body=${encodeURIComponent(enquiryText(s, tier))}`;
