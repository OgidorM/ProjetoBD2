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
                            <span className="text-2xl">📍</span>
                        </div>
                        <h4 className="font-modern-negra text-xl text-white">Localização</h4>
                        <p className="text-white/60">
                            Viseu, Portugal <br />
                            Sede Central
                        </p>
                    </div>

                    <div className="space-y-4">
                        <div className="w-12 h-12 bg-yellow/10 rounded-full flex items-center justify-center mx-auto text-yellow mb-6">
                            <span className="text-2xl">✉️</span>
                        </div>
                        <h4 className="font-modern-negra text-xl text-white">Email</h4>
                        <p className="text-white/60 hover:text-yellow transition-colors">
                            <a href="mailto:contato@cinetugal.pt">contato@cinetugal.pt</a>
                        </p>
                    </div>

                    <div className="space-y-4">
                        <div className="w-12 h-12 bg-yellow/10 rounded-full flex items-center justify-center mx-auto text-yellow mb-6">
                            <span className="text-2xl">📞</span>
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
