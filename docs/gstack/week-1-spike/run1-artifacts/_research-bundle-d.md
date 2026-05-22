# Bundle D — Regulatory & Tax (raw, from Researcher 2026-05-22)

## D1. PDP Law — UU 27/2022
- Enacted 17 Oct 2022; **fully enforced from 16-17 Oct 2024** (2-year transition ended).
- Extraterritorial: applies to foreign orgs processing Indonesian personal data.
- DPO required.
- Admin fines up to **2% annual revenue** (Art. 57).
- Criminal: falsification up to 6 yrs / IDR 60B; buying/selling personal data 5 yrs / IDR 50B.
- Cross-border transfer permitted with adequacy/contractual safeguards.
- Source: Schinder Law Firm 15 May 2024 — https://schinderlawfirm.com/blog/sanctions-and-compliance-with-indonesias-personal-data-protection-law-uu-pdp-by-october-16-2024/
- Source: FPF — https://fpf.org/blog/indonesias-personal-data-protection-bill-overview-key-takeaways-and-context/

## D2. PPN-PMSE (VAT on non-resident digital services)
- Effective 1 Jul 2020. Rate **12% from 1 Jan 2025** (deemed base 11/12 → effective ~11% of gross).
- Thresholds: IDR 600M/yr or IDR 50M/mo transactions; OR 12K/yr or 1K/mo Indonesian users.
- **251 collectors appointed as of Oct 2025** (Amazon, Google, MS, GitHub, Salesforce, Notion, Roblox, etc.). **No logistics SaaS visible.**
- Monthly remittance; IDR or USD.
- Source (primary): DJP — https://www.pajak.go.id/en/digitaltax
- Source: MUC Consulting — https://muc.co.id/en/article/indonesias-digital-tax-reaches-idr-4375-trillion-roblox-officially-appointed-as-pmse-vat-collector

## D3. PT PMA — paid-up capital
- BKPM Reg 5/2025: paid-up capital reduced from **IDR 10B → IDR 2.5B (~US$160K)** late 2025.
- Total investment plan still IDR 10B (~US$640K) registered via OSS-RBA.
- 100% foreign ownership permitted for KBLI 62xxx (software).
- LKPM reports required.
- Source: ASEAN Briefing 6 Oct 2025 — https://www.aseanbriefing.com/news/indonesia-lowers-paid-up-capital-for-foreign-investors-to-idr-2-5-billion/
- Source: Flado.id 11 Dec 2025 — https://flado.id/2025/12/11/new-update-for-foreign-investors-minimum-paid-up-capital-for-pt-pma-reduced-to-idr-2-5-billion-under-bkpm-regulation-no-5-2025/

## D4. PSE Lingkup Privat (PP 71/2019 + Permenkominfo 5/2020)
- Foreign operators serving Indonesian users must register via OSS.
- Threshold-based: IDR 600M annual transactions or 12K/1K user trip-wire (mirrors PMSE thresholds).
- Non-compliance → blocking (precedent: Jul 2022 Steam/Yahoo/PayPal blocked).
- Source: Indoservice — https://indoservice.co.id/electronic-system-operator-business-activities-pse/
- Source: LOC PDF — https://tile.loc.gov/storage-services/service/ll/llglrd/2025291256/2025291256.pdf

## D5. PPh 26 — withholding tax (cross-border)
- Default 20% on services/royalties to non-residents.
- **US-Indonesia treaty: royalties 10%, interest 10%, dividends 15/10%, branch profits 10%.**
- Requires Certificate of Domicile (CoD) from IRS; without CoD, Indonesian customer withholds at 20%.
- **SaaS classification risk**: ID tax authority may treat subscription fees as royalties → either way, customer withholds before paying foreign provider. This compresses realized revenue.
- Source: PwC Worldwide Tax Summaries — https://taxsummaries.pwc.com/indonesia/corporate/withholding-taxes
- Source: IRS US-Indonesia treaty — https://www.irs.gov/pub/irs-trty/indo.pdf

## D6. Data localization
- **No blanket localization** as of 2024-2025.
- PP 71/2019 had "strategic data" carve-out but implementing rules never broadly issued.
- Sector exceptions: financial (OJK), government, health — not applicable to logistics SaaS.
- Logistics SaaS can run on AWS/GCP Singapore/US; must document PDP adequacy basis.
- Source: ASEAN Briefing PDP guide — https://www.aseanbriefing.com/doing-business-guide/indonesia/company-establishment/personal-data-protection-law

## D-extra. CIT
- PT PMA CIT: **22% flat**.
- Small enterprises (<IDR 4.8B revenue): 0.5% final tax on turnover available.
- Source: PwC Pocket Tax Book 2024 — https://www.pwc.com/id/en/pocket-tax-book/english/pocket-tax-book-2024.pdf

## Implications for recommendation
- **Compliance load is manageable but real.** Four layers: PDP/DPO, PMSE-VAT, PSE registration, PPh-26 WHT. None individually fatal.
- **The PPh-26 royalty risk is the most economically painful**: 10% (best case w/ CoD) or 20% (no CoD) reduction on every IDR collected. Must price gross-up or accept margin hit.
- **PT PMA cost-of-entry dropped 75%** in late 2025 (IDR 10B→2.5B paid-up). This is *the* single most material recent change — makes a local entity option viable that was previously discouraging for a $1-10M ARR firm.
- **No data localization** = no cloud rebuild needed.
- **No logistics SaaS appears on the PMSE collector list** — implies none have scaled enough into ID to trigger the threshold yet (signal on market size).
