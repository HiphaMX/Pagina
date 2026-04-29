import styles from '../page.module.css';

export const metadata = {
  title: 'Aviso de Privacidad | Uro-Oncology',
  description: 'Conoce nuestro aviso de privacidad.',
};

export default function AvisoDePrivacidadPage() {
  return (
    <div className={styles.page}>
      <section className={styles.legalSection}>
        <div className="container">
          <div className={styles.legalContent}>
            <p>
              Uro-oncology, con portal de internet www.uro-oncology.com.mx, es responsable del uso y protección de sus datos personales, y al respecto le informamos lo siguiente:
            </p>

            <h3>FINALIDAD DE USO DE DATOS PERSONALES</h3>
            <p>
              De manera adicional, utilizaremos su información personal para las siguientes finalidades secundarias que no son necesarias para el servicio solicitado, pero que nos permiten y facilitan brindarle una mejor atención:
            </p>
            <ul>
              <li>a) Para poder enviar información sobre alguno de nuestros servicios</li>
              <li>b) Mercadotecnia o publicidad sobre nuestros servicios</li>
            </ul>
            <p>
              En caso de que no desee que sus datos personales sean tratados para estos fines secundarios, desde este momento usted nos puede comunicar lo anterior enviando un correo electrónico a: <strong>adal@uro-oncology.com.mx</strong>. La negativa para el uso de sus datos personales para estas finalidades no podrá ser un motivo para que le neguemos los servicios que solicita o contrata con nosotros.
            </p>

            <h3>DATOS PERSONALES SOLICITADOS</h3>
            <p>
              Para llevar a cabo las finalidades descritas en el presente aviso de privacidad, utilizaremos los siguientes datos personales:
            </p>
            <ul>
              <li>a) Datos de identificación</li>
              <li>b) Datos de contacto</li>
            </ul>

            <h3>¿PUEDE ACCEDER, RECTIFICAR O CANCELAR SUS DATOS PERSONALES U OPONERSE A SU USO?</h3>
            <p>
              Usted tiene derecho a conocer qué datos personales tenemos de usted, para qué los utilizamos y las condiciones del uso que les damos (Acceso). Asimismo, es su derecho solicitar la corrección de su información personal en caso de que no esté actualizada, sea inexacta o incompleta (Rectificación); que la eliminemos de nuestros registros o bases de datos cuando considere que la misma no está siendo utilizada adecuadamente (Cancelación); así como oponerse al uso de sus datos personales para fines específicos (Oposición). Estos derechos se conocen como derechos ARCO. Para el ejercicio de cualquiera de los derechos ARCO, usted deberá presentar su solicitud llamando por teléfono al número <strong>(33) 16013840</strong> o enviando un correo electrónico a la dirección: <strong>adal@uro-oncology.com.mx</strong>
            </p>
            <p>
              Los datos de contacto del departamento de datos personales, que está a cargo de dar trámite a las solicitudes de derechos ARCO, son los siguientes:
            </p>
            <ul>
              <li>a) Nombre del departamento de datos personales: Documentación</li>
              <li>b) Correo electrónico: adal@uro-oncology.com.mx</li>
              <li>c) Número telefónico: (33) 16013840</li>
            </ul>

            <h3>REVOCACIÓN DE CONSENTIMIENTO PARA EL USO DE SUS DATOS PERSONALES</h3>
            <p>
              Usted puede revocar el consentimiento que, en su caso, nos haya otorgado para el tratamiento de sus datos personales. Sin embargo, es importante que tenga en cuenta que no en todos los casos podremos atender su solicitud o concluir el uso de forma inmediata, ya que es posible que por alguna obligación legal requiramos seguir tratando sus datos personales. Asimismo, usted deberá considerar que para ciertos fines, la revocación de su consentimiento implicará que no le podamos seguir prestando el servicio que nos solicitó, o la conclusión de su relación con nosotros. Si desea revocar su consentimiento usted deberá presentar su solicitud a través del correo electrónico: <strong>adal@uro-oncology.com.mx</strong>
            </p>

            <h3>¿CÓMO PUEDE LIMITAR EL USO DE SU INFORMACIÓN PERSONAL?</h3>
            <p>
              Con objeto de que usted pueda limitar el uso y divulgación de su información personal, le ofrecemos los siguientes medios: Apegados a su derecho de elegir la información de su interés, se agrega la opción "Actualizar su información o salir de esta lista de correo" en el cuerpo de correo de todo arte gráfico que le sea enviado.
            </p>

            <h3>UTILIZACIÓN DE TECNOLOGÍAS DE RASTREO EN NUESTRO PORTAL WEB</h3>
            <p>
              Le informamos que en nuestra página de internet utilizamos cookies y otras tecnologías, a través de las cuales es posible monitorear su comportamiento como usuario de internet, así como brindarle un mejor servicio y experiencia al navegar en nuestra página. Los datos personales que recabamos a través de estas tecnologías, los utilizaremos para fines de tener estadísticas en la navegación de nuestra página, conocer mejor sus preferencias, brindarle mejores promociones de acuerdo a tus intereses y otras métricas de marketing digital. Los datos personales que obtenemos de estas tecnologías de rastreo son los siguientes:
            </p>
            <ul>
              <li>Región en la que se encuentra el usuario</li>
              <li>Tipo de navegador del usuario</li>
              <li>Tipo de sistema operativo del usuario</li>
              <li>Páginas visitadas y tiempo de navegación</li>
            </ul>

            <h3>¿CÓMO PUEDO CONOCER LOS CAMBIOS EN ESTE AVISO DE PRIVACIDAD?</h3>
            <p>
              El presente aviso de privacidad puede sufrir modificaciones, cambios o actualizaciones derivadas de nuevos requerimientos legales; de nuestras propias necesidades por los productos o servicios que ofrecemos; de nuestras prácticas de privacidad; de cambios en nuestro modelo de negocio, o por otras causas. Nos comprometemos a mantenerlo informado sobre los cambios que pueda sufrir el presente aviso de privacidad, a través de nuestra página web. En caso de haber alguna modificación, el procedimiento a través del cual se llevarán a cabo las notificaciones sobre cambios o actualizaciones al presente aviso de privacidad se realizará un comunicado oficial por parte de la empresa invitando al usuario a conocer los cambios en el aviso de privacidad, por medio de un envío de correo electrónico a nuestra base de datos de clientes y usuarios registrados.
            </p>

            <p className={styles.legalDate}>Última actualización: 01/05/2026</p>
          </div>
        </div>
      </section>
    </div>
  );
}
