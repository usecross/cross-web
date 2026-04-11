import { createDocsApp, DocsPage, HomePage } from '@usecross/docs'
import './styles.css'

createDocsApp({
  pages: {
    'docs/DocsPage': DocsPage,
    'HomePage': HomePage,
  },
  title: (title) => `${title} - Cross Web`,
})
