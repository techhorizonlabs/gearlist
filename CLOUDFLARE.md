# Host Gearlist on Cloudflare

Prompt for the agent that can edit the `gearlist.build` Cloudflare zone and GitHub Pages.

Set up https://gearlist.build as the public Gearlist site, hosted on Cloudflare, serving github.com/techhorizonlabs/gearlist.

Keep the existing catalog. Agent files already in the repo: llms.txt, llms-full.txt, resources.json, AGENTS.md. Skill install: npx skills add techhorizonlabs/gearlist. Issues stay off. Do not dump stars-queue onto the homepage. Do not print a Gatekeeper xattr command.

Live facts (checked 28 Oct 2026): Pages https://techhorizonlabs.github.io/gearlist/ returns 200 from main. NS for gearlist.build are already boyd.ns.cloudflare.com and laura.ns.cloudflare.com. Apex still points at Namecheap parking 162.255.119.231. www is a CNAME to parkingpage.namecheap.com. GitHub website field is already https://gearlist.build.

Preferred host: a Cloudflare Pages project on techhorizonlabs/gearlist, production branch main, custom domains gearlist.build and www.gearlist.build, Cloudflare-issued certificate. Remove the Namecheap URL forward on the apex.

If you stay on GitHub Pages instead, put these DNS-only records in the Cloudflare zone and add the custom domain in GitHub Pages: A @ 185.199.108.153, 185.199.109.153, 185.199.110.153, 185.199.111.153; CNAME www to techhorizonlabs.github.io.

Align with the current README groups and the kit social card. Australian English. No em or en dashes. Then re-check the live apex URL: the README, llms.txt and the og:image.
