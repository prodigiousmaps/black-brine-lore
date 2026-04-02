```yaml
---
type: faction
id: bb:faction:house-caldron
name: House Caldron
summary: >
  An old noble import–export house that presents itself as a stabilizing force
  in Black Brine’s volatile economy while quietly manipulating supply chains,
  prices, and competition to maintain dominance.
location: bb:location:black-brine

allies:
  - bb:faction:trade-authority

rivals:
  - bb:faction:black-sashes
  - bb:faction:independent-farmers
  - bb:faction:small-merchant-cooperatives

tags:
  - faction
  - noble-house
  - trade
  - import-export
  - economy
  - manipulation
  - black-brine
  - sedna

overview: >
  House Caldron is a long-established noble family whose wealth predates Black
  Brine’s rise as a pirate haven. While piracy injects chaos and wealth into the
  city, House Caldron thrives through predictability—controlling logistics,
  insurance, warehousing, and mainland trade relationships that pirates and
  small merchants cannot easily access.

business_interests:
  import_export:
    description: >
      Bulk movement of mainland goods (grain, tools, textiles, luxuries) into
      Black Brine and export of Sedna’s regulated resources through licensed
      channels.
    advantages:
      - Preferential docking contracts
      - Mainland credit relationships
      - Long-term shipping insurance
  warehousing:
    description: >
      Ownership of bonded warehouses near the docks used to store goods pending
      Trade Authority inspection.
    leverage:
      - Storage fees pressure small operators
      - Selective “delays” for competitors
  shipping_insurance:
    description: >
      Private underwriting for caravans and ships, framed as risk mitigation in
      pirate waters.
    hidden_function:
      - Intelligence gathering on routes and cargo
      - Identifying vulnerable targets
  price_control:
    description: >
      Use of intermediaries to manipulate market access and discourage
      independent sellers without overt violence.

methods:
  intimidation:
    description: >
      Non-lethal pressure campaigns designed to appear as bad luck, banditry,
      or environmental hazard.
    tools:
      - Paid guard abandonment
      - Engineered beast encounters
      - Legal harassment via contracts
  intermediaries:
    description: >
      House Caldron never acts directly. All actions are laundered through
      fixers, hired crews, and deniable assets.
  obfuscation:
    description: >
      Financial interests are deliberately fragmented across shell companies,
      silent partners, and mainland accounts.

key_figures:
  - name: Marcellus Caldron
    title: Head of House Caldron
    description: >
      Public face of the family—measured, diplomatic, and careful to remain
      within the letter of Trade Authority law.
  - name: Ossian
    title: External Fixer
    description: >
      A ruthless operative employed exclusively by House Caldron. Not a family
      member. Highly intelligent, obsessive, and contemptuous of the nobility
      he serves. Executes long-term destabilization campaigns through hired
      agents, blackmail, and targeted disruption.

current_operations:
  eastern_sedna:
    description: >
      Campaign to prevent farmers from bypassing wholesalers and forming
      cooperatives.
    objectives:
      - Preserve price control
      - Undermine independent distribution
      - Avoid Trade Authority scrutiny
    status: >
      Escalating after initial intimidation failed; opposition growing more
      resilient.

role_in_society:
  citizens: >
    Seen as distant but respectable—blamed vaguely for “how things are” rather
    than specific harms.
  merchants: >
    Both patron and threat; access to Caldron contracts brings stability at the
    cost of independence.
  authorities: >
    Maintains careful compliance to avoid House of Questions investigation.

rumors:
  - House Caldron knows about raids before they happen.
  - Their insurance never covers the people who need it most.
  - Someone outside the family truly runs their dirty work.

connections:
  - bb:location:black-brine
  - bb:faction:black-brine-trade-authority
  - bb:faction:black-sashes
```
