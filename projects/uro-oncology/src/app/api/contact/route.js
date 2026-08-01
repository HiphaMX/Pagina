import nodemailer from 'nodemailer';

export async function POST(req) {
  try {
    const { nombre, apellido, telefono, email, mensaje, honeypot, recaptcha_token } = await req.json();

    if (honeypot) {
      console.warn("[SPAM DETECTED] Honeypot field filled for Uro-Oncology contact form.");
      return new Response(JSON.stringify({ success: true }), { status: 200 });
    }

    // Validar reCAPTCHA v3 de forma fail-safe
    const secretKey = process.env.UROONCOLOGY_RECAPTCHA_SECRET_KEY || process.env.RECAPTCHA_SECRET_KEY;
    if (secretKey) {
      if (!recaptcha_token) {
        console.warn("[SPAM DETECTED] Missing or empty reCAPTCHA token for Uro-Oncology contact form.");
        return new Response(JSON.stringify({ success: true }), { status: 200 });
      }
      try {
        const verifyRes = await fetch("https://www.google.com/recaptcha/api/siteverify", {
          method: "POST",
          headers: { "Content-Type": "application/x-www-form-urlencoded" },
          body: `secret=${secretKey}&response=${recaptcha_token}`
        });
        const verifyData = await verifyRes.json();
        if (!verifyData.success || verifyData.score < 0.5) {
          console.warn(`[SPAM DETECTED] reCAPTCHA validation failed for Uro-Oncology. Success: ${verifyData.success}, Score: ${verifyData.score}`);
          return new Response(JSON.stringify({ success: true }), { status: 200 });
        }
      } catch (err) {
        console.error("Error validating reCAPTCHA for Uro-Oncology:", err);
      }
    } else {
      console.warn("[SECURITY WARNING] UROONCOLOGY_RECAPTCHA_SECRET_KEY is not configured in environment variables. Verification bypassed!");
    }

    const fullName = `${nombre} ${apellido}`;

    const transporter = nodemailer.createTransport({
      host: process.env.SMTP_HOST || 'smtp.gmail.com', // Replace with proper host if not Gmail
      port: Number(process.env.SMTP_PORT) || 465,
      secure: Number(process.env.SMTP_PORT) === 465, // true for 465, false for other ports
      auth: {
        user: process.env.SMTP_USER,
        pass: process.env.SMTP_PASS,
      },
      tls: {
        rejectUnauthorized: false,
      }
    });

    // 1. Email to Doctor
    const mailToDoctor = {
      from: `"Uro-Oncology Web" <${process.env.SMTP_USER}>`,
      to: 'adal@uro-oncology.com.mx', // Doctor's email
      subject: `Nuevo paciente desde la web: ${fullName}`,
      html: `
        <h2>Nuevo contacto desde sitio web Uro-Oncology</h2>
        <p><strong>Nombre:</strong> ${fullName}</p>
        <p><strong>Teléfono:</strong> ${telefono}</p>
        <p><strong>Email:</strong> ${email}</p>
        <p><strong>Mensaje:</strong><br/> ${mensaje || 'Sin mensaje'}</p>
      `,
    };

    // 2. Email to Prospect
    const mailToProspect = {
      from: `"Dr. Adalberto Castro Alfaro" <${process.env.SMTP_USER}>`,
      to: email,
      subject: `Hemos recibido tu solicitud - Uro-Oncology`,
      html: `
        <div style="font-family: Arial, sans-serif; color: #333;">
          <h2 style="color: #001b2e;">Hola ${nombre},</h2>
          <p>Hemos recibido tus datos correctamente a través de nuestro portal web.</p>
          <p>El Dr. Adalberto Castro Alfaro y su equipo médico revisarán tu caso a la brevedad y nos pondremos en contacto contigo al número <strong>${telefono}</strong> para definir los siguientes pasos o programar tu cita de diagnóstico.</p>
          <p>Si se trata de una emergencia, por favor comunícate inmediatamente al <strong>331 6013 840</strong>.</p>
          <br/>
          <p>Atentamente,<br/><strong>Equipo Uro-Oncology</strong></p>
          <p><em>El pulso humano de la cirugía robótica</em></p>
        </div>
      `,
    };

    // If SMTP credentials aren't set up yet, we'll return a simulated success in dev
    if (!process.env.SMTP_USER || !process.env.SMTP_PASS) {
      console.warn("SMTP credentials not configured. Simulating email send.");
      console.log("To Doctor:", mailToDoctor);
      console.log("To Prospect:", mailToProspect);
      return new Response(JSON.stringify({ success: true, simulated: true }), { status: 200 });
    }

    await transporter.sendMail(mailToDoctor);
    await transporter.sendMail(mailToProspect);

    return new Response(JSON.stringify({ success: true }), { status: 200 });
  } catch (error) {
    console.error('Error sending email:', error);
    return new Response(JSON.stringify({ success: false, error: error.message }), { status: 500 });
  }
}
