import { useState, useEffect } from 'react'
import { HomePage, HomeHeader, HomeHero, HomeFeatures, HomeCTA, HomeFooter } from '@usecross/docs'
import { Logo } from '../components/Logo'

export default function Home(props: any) {
  const [showFullLogo, setShowFullLogo] = useState(false)
  const navLinks = props.navLinks ?? [{ label: 'Docs', href: '/docs' }]

  useEffect(() => {
    const handleScroll = () => {
      setShowFullLogo(window.scrollY > 250)
    }

    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  return (
    <HomePage {...props} navLinks={navLinks}>
      <HomeHeader renderLogo={() => <Logo showFull={showFullLogo} />} />
      <HomeHero />
      <HomeFeatures />
      <HomeCTA />
      <HomeFooter />
    </HomePage>
  )
}
