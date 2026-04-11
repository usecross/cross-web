import { APIPage, createDocsApp, DocsPage, HomePage } from '@usecross/docs'
import './styles.css'

createDocsApp({
  pages: {
    'docs/DocsPage': DocsPage,
    'HomePage': HomePage,
    'api/APIPage': APIPage,
  },
  title: (title) => `${title} - Cross Web`,
})
