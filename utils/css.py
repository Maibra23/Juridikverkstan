"""Appens CSS-mall, utbruten ur utils/ui.py för att hålla den filen under
radtaket i implementationsplanen (planens Global Constraints, 800 rader).

CSS_MALL är en formatbar sträng: `{BLACK}`-liknande platshållare fylls i av
inject_css() i utils/ui.py, som äger paletten och anropar `.format(...)` på
konstanten innan den injiceras med st.html. Denna modul har inget eget
Streamlit-beroende och innehåller ingen logik, bara mallen.
"""

from __future__ import annotations

CSS_MALL = """
        <style>
        :root {{
            --bl: {BLACK}; --perg: {PARCHMENT}; --panel: {PANEL};
            --ram: {BORDER}; --bla: {BLUE}; --guld: {GOLD};
            --gron: {GREEN}; --varn-fg: {WARN_FG}; --varn-bg: {WARN_BG};
            --varn-mork: {WARN_DARK}; --fel: {ERROR};

            /* Typskala (design_system.md 2.1). Sex steg, en roll var. */
            --t-hero: 28px;     /* sidrubrik, en per sida */
            --t-h2: 22px;       /* avsnittsrubrik */
            --t-h3: 18px;       /* kortrubrik */
            --t-brod: 17px;     /* brödtext, scenarier */
            --t-ui: 15px;       /* kontroller, kortmetadata */
            --t-etikett: 13px;  /* kapitäler, chips, metadata */

            /* Spacingskala, 4px-bas (design_system.md 2.2). Regeln: avstånd
               INOM en grupp är alltid mindre än avstånd MELLAN grupper. */
            --s1: 4px; --s2: 8px; --s3: 12px; --s4: 16px;
            --s5: 24px; --s6: 32px; --s7: 48px;

            /* Typsnittsstackar (design_system.md 2). Endast systemtypsnitt:
               inga typsnittsfiler, ingen CDN. */
            --font-serif: Georgia, "Iowan Old Style", "Times New Roman", serif;
            --font-mono: ui-monospace, "SF Mono", Menlo, Consolas, monospace;
            --font-sans: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;

            /* Dämpade toner och textguld (design_system.md 1). Guld som TEXT
               använder den mörkare nyansen: --guld klarar bara 3.2:1 och duger
               för ramar och grafnoder, inte för 13px-text. */
            --gra: #6B6459; --gra-dampad: #736C5E; --guld-text: #8A6608;

            /* Hörnradier och kortskugga. */
            --r1: 6px; --r2: 10px; --r3: 12px;
            --skugga: 0 1px 3px rgba(26,35,50,.06);
        }}
        /* Text bara för skärmläsare, t.ex. stepperns tillstånd och att en
           länk öppnas i ny flik. Standardmönstret för visuellt dold text. */
        .sr-only {{
            position: absolute; width: 1px; height: 1px; padding: 0;
            margin: -1px; overflow: hidden; clip: rect(0, 0, 0, 0);
            white-space: nowrap; border: 0;
        }}
        /* Synlig fokusring för tangentbordet på appens egna länkar. */
        .jok-chip:focus-visible, .jok-lagkort a:focus-visible {{
            outline: 2px solid var(--bla); outline-offset: 2px;
        }}
        /* Sidlänkar i innehållsytan (Kunskapstest, "Öva i modulen") ska se
           ut som länkar. Sidopanelens länkar berörs inte: de är navigering
           och har sin egen stil (design_system.md 4.1). */
        [data-testid="stMain"] [data-testid="stPageLink"] a p {{
            color: var(--bla); font-weight: 600;
        }}
        [data-testid="stMain"] [data-testid="stPageLink"] a:hover p {{
            text-decoration: underline;
        }}
        .jok-hero {{
            max-width: 46rem; margin: 0 0 1.5rem 0;
        }}
        .jok-hero .eyebrow {{
            font-family: var(--font-mono); font-size: var(--t-etikett);
            letter-spacing: .12em; color: var(--bla); text-transform: uppercase;
        }}
        .jok-hero h1 {{
            font-family: var(--font-serif); color: var(--bl);
            font-size: var(--t-hero); line-height: 1.2; margin: .3rem 0 .6rem 0;
        }}
        .jok-hero p {{
            font-size: var(--t-brod); line-height: 1.65; color: var(--bl); margin: 0;
        }}
        .jok-section {{ margin: 1.8rem 0 .6rem 0; }}
        .jok-section .eyebrow {{
            font-family: var(--font-mono); font-size: var(--t-etikett);
            letter-spacing: .12em; color: var(--bla); text-transform: uppercase;
        }}
        .jok-section h2 {{
            font-family: var(--font-serif); color: var(--bl);
            font-size: var(--t-h2); margin: .2rem 0 0 0;
        }}
        .jok-pipeline {{ display: flex; flex-wrap: wrap; gap: .5rem; margin: .5rem 0; }}
        .jok-pipeline span {{
            background: var(--panel); border: 1px solid var(--ram);
            border-radius: 999px; padding: .35rem .9rem; font-size: var(--t-etikett);
        }}
        /* Metodraden på startsidan: text, inte knappar. */
        .jok-metod {{
            display: flex; flex-wrap: wrap; gap: var(--s2) var(--s5);
            margin: var(--s2) 0 var(--s4) 0; font-size: var(--t-ui); color: var(--bl);
        }}
        .jok-metod .nr {{
            font-family: var(--font-mono); font-size: var(--t-etikett);
            color: var(--bla); font-weight: 700; margin-right: var(--s1);
        }}
        /* Framstegstal på startsidan. */
        .jok-stat-rad {{
            display: flex; flex-wrap: wrap; gap: var(--s5);
            margin: var(--s3) 0 var(--s4) 0;
        }}
        .jok-stat .tal {{
            font-family: var(--font-serif); font-size: var(--t-h2);
            font-variant-numeric: lining-nums tabular-nums; color: var(--bl);
            line-height: 1.2;
        }}
        .jok-stat .etikett {{ font-size: var(--t-etikett); color: var(--gra); }}
        .jok-chip {{
            display: inline-flex; align-items: center; gap: .3rem;
            font-family: var(--font-mono); font-size: var(--t-etikett);
            border: 1px solid var(--guld); border-radius: 999px;
            padding: .15rem .6rem; color: var(--bl); text-decoration: none;
            background: #FFFDF7;
        }}
        .jok-chip.ovarifierad {{
            border-color: var(--varn-mork); background: var(--varn-bg);
        }}
        .jok-varning, .jok-info {{
            border-radius: var(--r2); padding: .8rem 1rem; margin: .6rem 0;
            font-size: var(--t-ui); line-height: 1.55; max-width: 46rem;
        }}
        .jok-varning {{ background: var(--varn-bg); border: 1px solid var(--varn-mork); color: var(--bl); }}
        .jok-info {{ background: #EAF1F7; border: 1px solid var(--bla); }}
        .jok-tutortext {{
            background: var(--panel); border: 1px solid var(--ram);
            border-left: 3px solid var(--bla); border-radius: var(--r2);
            padding: .9rem 1.2rem; margin: .6rem 0; max-width: 46rem;
            font-size: var(--t-brod); line-height: 1.6; color: var(--bl);
            font-family: var(--font-serif); font-variant-numeric: lining-nums;
        }}
        .jok-tutortext p {{ margin: 0 0 .6rem 0; }}
        .jok-tutortext p:last-child {{ margin-bottom: 0; }}
        .jok-tutortext .rnts-rubrik {{
            font-variant: small-caps; letter-spacing: .05em;
            color: var(--bla); font-weight: 700;
        }}
        .jok-varning ul {{ margin: .4rem 0 .2rem 1.1rem; padding: 0; }}
        .jok-case {{
            background: var(--panel); border: 1px solid var(--ram);
            border-top: 3px solid var(--guld); border-radius: var(--r3);
            padding: 1.1rem 1.3rem; margin: .6rem 0; max-width: 46rem;
            box-shadow: var(--skugga);
        }}
        .jok-case h3 {{
            font-family: var(--font-serif); color: var(--bl);
            font-size: var(--t-h3); margin: 0 0 .2rem 0;
        }}
        .jok-case .meta {{ font-size: var(--t-etikett); color: var(--gra); margin-bottom: .5rem; }}
        .jok-case p {{ font-family: var(--font-serif); font-variant-numeric: lining-nums;
            font-size: var(--t-brod); line-height: 1.65; color: var(--bl); margin: 0; }}
        .jok-rnts {{ margin: .4rem 0 .8rem 0; }}
        /* Vågrät stepper ovanför RNTS-fälten i rättsfallsvyn. */
        .jok-rnts.vagrat {{
            display: flex; flex-wrap: wrap; gap: var(--s1) var(--s4);
            margin: 0 0 var(--s3) 0;
        }}
        .jok-rnts .steg {{
            display: flex; align-items: center; gap: .55rem;
            font-size: var(--t-etikett); color: var(--bl); padding: .22rem 0;
        }}
        .jok-rnts .ikon {{
            display: inline-flex; align-items: center; justify-content: center;
            width: 1.25rem; height: 1.25rem; border-radius: 999px;
            font-size: var(--t-etikett); line-height: 1; flex: 0 0 auto;
            border: 2px solid var(--ram); background: var(--panel); color: transparent;
        }}
        .jok-rnts .steg.pagar .ikon {{
            border-color: var(--bla); background: var(--bla);
        }}
        .jok-rnts .steg.godkand .ikon {{
            border-color: var(--gron); background: var(--gron);
        }}
        /* Bocken ritas som två kanter roterade 45 grader, inte som en teckenglyf (U+2713). */
        .jok-rnts .steg.godkand .ikon::after {{
            content: ""; display: block; width: .3rem; height: .55rem;
            margin: .12rem auto 0 auto; transform: rotate(45deg);
            border-right: 2px solid #fff; border-bottom: 2px solid #fff;
        }}
        .jok-rnts .steg.behover-mer .ikon {{
            border-color: var(--varn-mork); background: var(--varn-bg);
        }}
        /* Utropstecknet som stapel och punkt, av samma skäl som bocken. */
        .jok-rnts .steg.behover-mer .ikon::after {{
            content: ""; display: block; width: 2px; height: .45rem;
            margin: .2rem auto 0 auto; background: var(--varn-mork);
            box-shadow: 0 .18rem 0 0 var(--varn-mork);
        }}
        /* Navigeringshierarki i sidopanelen (design_system.md 4.1).
           Nivåerna skiljs åt med indrag, storlek och färgstyrka, inte med
           ikoner: huvudkategori (versaler, blå) > underkategori (bläck)
           > undergren (grå) > modul (st.page_link). */
        /* Sidopanelens vertikala rytm följer spacingskalan (2.2): avståndet
           MELLAN grupper är alltid större än avståndet INOM en grupp, så
           närheten bär strukturen utan att kräva ramar eller linjer. */
        /* Varumärket överst i sidopanelen (design_system.md 4.1). */
        .jok-varumarke {{ margin: 0 0 var(--s2) 0; }}
        .jok-varumarke .namn {{
            font-family: var(--font-serif); font-size: var(--t-h3);
            font-weight: 700; color: var(--bl); line-height: 1.3;
        }}
        .jok-varumarke .tagline {{
            font-size: var(--t-etikett); color: var(--gra); margin-top: var(--s1);
        }}
        .jok-nav-kategori {{
            font-family: var(--font-mono);
            font-size: var(--t-etikett); letter-spacing: .1em; text-transform: uppercase;
            color: var(--bla); font-weight: 700;
            margin: var(--s5) 0 var(--s1) 0;
        }}
        .jok-nav-under {{
            font-size: var(--t-etikett); font-weight: 600; color: var(--bl);
            margin: var(--s3) 0 var(--s1) 0;
        }}
        .jok-nav-gren {{
            font-size: var(--t-etikett); font-weight: 600; color: var(--gra);
            letter-spacing: .02em; margin: var(--s2) 0 var(--s1) var(--s3);
        }}
        .jok-nav-kommer {{
            font-size: var(--t-etikett); color: var(--gra-dampad);
            margin: var(--s1) 0 var(--s1) var(--s3);
        }}
        /* Förfäderna till den öppna sidan får full bläckvikt, så att studenten
           hittar sin plats i ett fyra nivåer djupt träd. Ingen färg, ingen
           ikon: guld är reserverat för lagrum. */
        .jok-nav-under.aktiv, .jok-nav-gren.aktiv {{
            color: var(--bl); font-weight: 700;
        }}
        .jok-nav-kategori.aktiv {{ color: var(--bl); }}
        /* Färglegend för taxonomigrafen: riktiga färgrutor, inte prosa. */
        .jok-legend {{
            display: flex; flex-wrap: wrap; gap: .5rem 1.1rem;
            margin: .6rem 0 1rem 0; font-size: var(--t-etikett); color: var(--bl);
        }}
        .jok-legend-post {{ display: inline-flex; align-items: center; gap: .4rem; }}
        .jok-swatch {{
            display: inline-block; width: .85rem; height: .85rem;
            border-radius: 3px; border: 1px solid rgba(26,35,50,.25);
            flex: 0 0 auto;
        }}

        /* Lagkort i områdesträdet (flik Systemet). */
        .jok-lagkort {{
            background: var(--panel); border: 1px solid var(--ram);
            border-left: 3px solid var(--guld); border-radius: var(--r2);
            padding: .8rem 1rem; margin: .5rem 0; max-width: 46rem;
        }}
        .jok-lagkort h4 {{
            font-family: var(--font-serif);
            font-size: var(--t-h3); color: var(--bl); margin: 0 0 .1rem 0;
        }}
        .jok-lagkort .sfs {{
            font-family: var(--font-mono);
            font-size: var(--t-etikett); color: var(--gra);
        }}
        .jok-lagkort p {{ font-size: var(--t-ui); line-height: 1.55; margin: .45rem 0 0 0; }}
        .jok-lagkort .nar {{ font-size: var(--t-etikett); color: #4A453D; margin-top: .4rem; }}
        .jok-lagkort .nar strong {{ color: var(--bla); }}
        .jok-lagkort .avsnitt {{
            margin-top: .7rem; padding-top: .6rem;
            border-top: 1px solid rgba(107, 100, 89, .18);
        }}
        .jok-lagkort .avsnittsrubrik {{
            font-size: var(--t-etikett); letter-spacing: .08em; text-transform: uppercase;
            color: var(--gra); display: flex; justify-content: space-between;
            gap: 1rem; margin-bottom: .35rem;
        }}
        .jok-lagkort .tackning {{ text-transform: none; letter-spacing: 0; }}
        .jok-lagkort .kapitelrad {{
            font-size: var(--t-etikett); font-weight: 600; color: var(--bla);
            margin: .45rem 0 .2rem 0;
        }}
        .jok-lagkort .avsnittsrad {{
            display: flex; gap: .6rem; font-size: var(--t-etikett); line-height: 1.5;
            padding: .1rem 0 .1rem .6rem;
        }}
        .jok-lagkort .avsnittsrad .spann {{
            flex: 0 0 6.5rem; color: var(--guld-text); font-variant-numeric: tabular-nums;
            text-decoration: none; font-weight: 600;
        }}
        .jok-lagkort .avsnittsrad .spann:hover {{ text-decoration: underline; }}
        .jok-lagkort .avsnittstext {{ color: #4A453D; }}
        .jok-lagkort .avsnittsnot {{
            font-size: var(--t-etikett); color: var(--gra); margin-top: .5rem; font-style: italic;
        }}

        /* Begreppskort (flik Nyckelbegrepp). */
        .jok-begrepp {{
            background: var(--panel); border: 1px solid var(--ram);
            border-radius: var(--r3); padding: 1rem 1.2rem; margin: .5rem 0 .2rem 0;
            max-width: 46rem; box-shadow: var(--skugga);
        }}
        .jok-begrepp h3 {{
            font-family: var(--font-serif);
            font-size: var(--t-h3); color: var(--bl); margin: 0 0 .1rem 0;
        }}
        .jok-begrepp .kapitel {{
            font-family: var(--font-mono);
            font-size: var(--t-etikett); letter-spacing: .08em; text-transform: uppercase;
            color: var(--bla);
        }}
        .jok-begrepp .falt {{ margin: .7rem 0 0 0; }}
        .jok-begrepp .falt .etikett {{
            font-variant: small-caps; letter-spacing: .05em; font-weight: 700;
            color: var(--bla); font-size: var(--t-etikett); display: block;
            margin-bottom: .15rem;
        }}
        .jok-begrepp .falt p {{
            font-family: var(--font-serif); font-variant-numeric: lining-nums;
            font-size: var(--t-brod); line-height: 1.6; color: var(--bl); margin: 0;
        }}
        /* Skillnadsraden för kontrastpar: en enda framhävd rad. */
        .jok-begrepp .skillnad {{
            background: #F5F1EA; border-left: 3px solid var(--bla);
            border-radius: 0 var(--r1) var(--r1) 0; padding: .5rem .8rem; margin: .7rem 0 0 0;
            font-size: var(--t-ui); line-height: 1.5;
        }}
        .jok-begrepp .igenkanning {{
            background: #FFFDF7; border: 1px dashed var(--guld);
            border-radius: var(--r2); padding: .6rem .8rem; margin-top: .7rem;
        }}

        .jok-footer {{
            margin-top: 2rem; padding-top: 1rem; border-top: 1px solid var(--ram);
            font-size: var(--t-etikett); color: var(--gra); max-width: 46rem;
        }}

        /* Vilket RNTS-steg en aktivitet tränar. Dämpad kapitälrad: informativ
           en gång, därefter tyst. */
        .jok-tranar {{
            font-family: var(--font-mono);
            font-size: var(--t-etikett); letter-spacing: .1em;
            text-transform: uppercase; color: var(--gra);
            margin: var(--s3) 0 var(--s2) 0;
        }}

        /* Smal skärm (telefon). Typskalan och spacingskalan gäller fortfarande;
           bara stegen byts, så att inget nytt värde införs. */
        @media (max-width: 640px) {{
            .jok-hero h1 {{ font-size: var(--t-h2); }}
            .jok-case, .jok-lagkort, .jok-begrepp {{ padding: var(--s4); }}
            .jok-stat-rad {{ gap: var(--s4); }}
            .jok-lagkort .avsnittsrad .spann {{ flex-basis: 5rem; }}
            .jok-hero .eyebrow {{ letter-spacing: .08em; }}
        }}
        </style>
        """
