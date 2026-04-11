import { APIPage, DocsPage, HomePage } from '@usecross/docs'
import { createDocsServer } from '@usecross/docs/ssr'

createDocsServer({
  pages: {
    'docs/DocsPage': DocsPage,
    'HomePage': HomePage,
    'api/APIPage': APIPage,
  },
  title: (title) => `${title} - Cross Web`,
})
