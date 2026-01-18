import React, {useRef} from "react";
import {useGSAP} from "@gsap/react";
import gsap from "gsap";
import {SplitText} from "gsap/all";
import {useMediaQuery} from "react-responsive";

const Hero = () => {
    const videoRef = useRef();

    const isMobile = useMediaQuery({maxWidth: 767});

    useGSAP(() => {
        const heroSplit = new SplitText('.title', {type: 'chars, words'});
        const paragraphSplit = new SplitText('.subtitle', {type: 'lines'});

        heroSplit.chars.forEach((char) => char.classList.add('text-gradient'));

        gsap.from(heroSplit.chars, {
            yPercent: 100,
            duration: 1.8,
            ease: 'expo.out',
            stagger: 0.10,
        });

        gsap.from(paragraphSplit.lines, {
            opacity: 0,
            yPercent: 100,
            duration: 1.8,
            ease: 'expo.out',
            stagger: 0.06,
            delay: 1,
        });

        gsap.timeline({
            scrollTrigger: {
                trigger: '#hero',
                start: 'top top',
                end: 'bottom top',
                scrub: true,
            }
        })

        const startValue = isMobile ? 'top 50%' : 'center 50%';
        const endValue = isMobile ? 'top 150%' : 'bottom+=250 top';

        const tl = gsap.timeline({
            scrollTrigger: {
                trigger: 'video',
                start: startValue,
                end: endValue,
                scrub: true,
                pin:true,
            }
        })
        videoRef.current.onloadedmetadata = () => {
            tl.to(videoRef.current, {
                currentTime: videoRef.current.duration,
            })
            .to('.video', {
                opacity: 0,
                ease: 'none'
            })
        }
    }, []);
    return (
        <>
            <section id="hero" className="noisy">
                <div className="absolute inset-0 opacity-50"></div>

                <h1 className="title">Cinetugal</h1>

                <div className="body">
                    <div className="content">
                        <div className="space-y-5 hidden md:block">
                            <p>O retro no futuro</p>
                            <p className="subtitle">
                              O Cinema Favorito <br /> dos Portugueses
                            </p>
                        </div>

                        <div className="view-cocktails">
                            <p className="subtitle">
                                Os teus clássicos favoritos disponíveis num só lugar.
                            </p>
                            <a href="#classic-movies">Ver Filmes</a>
                        </div>
                    </div>
                </div>
            </section>
            <div className="video absolute inset-0">
                <video
                    ref={videoRef}
                    src="/videos/popcorn.mp4"
                    muted
                    playsInline
                    preload="auto"
                />
            </div>
        </>
    )
}
export default Hero;
