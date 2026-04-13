import { createDocsApp, DocsPage } from '@usecross/docs'
import Home from './pages/Home'
import './styles.css'

createDocsApp({
  pages: {
    'docs/DocsPage': DocsPage,
    'HomePage': Home,
  },
  title: (title) => `${title} - Cross Web`,
})
