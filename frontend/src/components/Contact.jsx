import React from 'react';

const Contact = () => {
    return (
        <section id="contact">
            <div className="noisy absolute inset-0 opacity-20 pointer-events-none"></div>
            
            <div className="content relative z-10">
                <div className="space-y-4">
                    <h3 className="uppercase tracking-[0.3em] text-yellow font-bold text-sm">Entre em Contacto</h3>
                    <h2 className="text-white">
                        Estamos aqui para <br /> melhorar a sua experiência
                    </h2>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-12 max-w-5xl mx-auto py-20">
                    <div className="space-y-4">
                        <div className="w-12 h-12 bg-yellow/10 rounded-full flex items-center justify-center mx-auto text-yellow mb-6">
                            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                            </svg>
                        </div>
                        <h4 className="font-modern-negra text-xl text-white">Localização</h4>
                        <p className="text-white/60">
                            Viseu, Portugal <br />
                            Sede Central
                        </p>
                    </div>

                    <div className="space-y-4">
                        <div className="w-12 h-12 bg-yellow/10 rounded-full flex items-center justify-center mx-auto text-yellow mb-6">
                            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                            </svg>
                        </div>
                        <h4 className="font-modern-negra text-xl text-white">Email</h4>
                        <p className="text-white/60 hover:text-yellow transition-colors">
                            <a href="mailto:contato@cinetugal.pt">contato@cinetugal.pt</a>
                        </p>
                    </div>

                    <div className="space-y-4">
                        <div className="w-12 h-12 bg-yellow/10 rounded-full flex items-center justify-center mx-auto text-yellow mb-6">
                            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                            </svg>
                        </div>
                        <h4 className="font-modern-negra text-xl text-white">Telefone</h4>
                        <p className="text-white/60">
                            +351 210 000 000 <br />
                            Seg-Sex, 10h-22h
                        </p>
                    </div>
                </div>

                <div className="pt-10 border-t border-white/5">
                    <p className="text-white/20 text-sm uppercase tracking-widest">
                        &copy; 2026 Cinemas de Portugal. Todos os direitos reservados.
                    </p>
                </div>
            </div>
        </section>
    );
};

export default Contact;
