// pages/asistente-voz.js o app/asistente-voz/page.js (dependiendo de tu estructura)

import Head from 'next/head';
import VoiceAssistant from '@/components/voice-assistant/voice-assistant';

export default function AsistenteVoz() {
  return (
    <>
      <Head>
        <title>Asistente Médico por Voz</title>
        <meta name="description" content="Sistema de asistencia médica con IA por voz" />
      </Head>
      
      <div className="min-h-screen bg-gray-100 py-8">
        <div className="container mx-auto px-4">
          <VoiceAssistant />
        </div>
      </div>
    </>
  );
}