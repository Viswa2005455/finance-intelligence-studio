import { describe, expect, it } from 'vitest';
import catalog from '../../../backend/app/payments/service_catalog.json';
import { SERVICES } from './services';

// The server charges from service_catalog.json; the website shows prices from services.ts.
// If they drift, customers would see one price and pay another.
describe('service prices', () => {
  it('match the server catalogue for every service and package', () => {
    const cat = catalog as Record<string, { id: number; title: string; tiers: Record<string, { price: number; days: number }> }>;
    expect(Object.keys(cat).sort()).toEqual(SERVICES.map((s) => s.slug).sort());
    for (const s of SERVICES) {
      expect(cat[s.slug].id).toBe(s.id);
      for (const t of s.tiers) expect(cat[s.slug].tiers[t.name]).toEqual({ price: t.price, days: t.days });
    }
  });
});
