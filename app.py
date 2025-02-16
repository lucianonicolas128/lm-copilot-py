import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import os
import requests
from fpdf import FPDF
import sqlite3



#
#
#
# Conectar a la base de datos SQLite
conn = sqlite3.connect('stickers.db')
c = conn.cursor()

# Crear la tabla si no existe
c.execute('''
    CREATE TABLE IF NOT EXISTS stickers (
        id INTEGER PRIMARY KEY,
        document_name TEXT,
        name TEXT,
        font TEXT,
        text_border_color1 TEXT,
        text_color1 TEXT,
        font_size_input1 INTEGER,
        border_thickness1 INTEGER,
        text_margin_top1 INTEGER,
        text_alignment1 TEXT,
        image_url TEXT,
        bg_color TEXT,
        text_color2 TEXT,
        text_border_color2 TEXT,
        font_size_input2 INTEGER,
        border_thickness2 INTEGER,
        text_margin_top2 INTEGER,
        text_alignment2 TEXT,
        icon_url TEXT
    )
''')
conn.commit()
#
#
#
# Configurar el ancho del contenedor de la app
st.set_page_config(layout="wide") 

section = st.sidebar.selectbox("Selecciona una sección", ["Generar Stickers", "Otra Sección"])


if section == "Generar Stickers":

  # Título de la app
  st.title("Generador de Stickers Escolares")

  stickers = c.execute('SELECT id, document_name, image_url FROM stickers').fetchall()


  # Input para el nombre del documento
  document_name = st.text_input("Nombre del documento", value=st.session_state.get('document_name', ''))



  # Secciones de configuración y vista previa
  col1, col2 = st.columns(2)

  with col1:
      st.header("Configuración de Sticker 1")

      # Input para cargar imagen de fondo
      # uploaded_image = st.file_uploader("Subir imagen de fondo", type=["png", "jpg", "jpeg"])
      image_url = st.text_input("Pegar URL de imagen de fondo", value=st.session_state.get('image_url', ''))


      # Inputs de texto y selección de fuente
      col_name, col_font = st.columns(2)
      with col_name:
          name = st.text_input("Escribe el nombre para el sticker", value=st.session_state.get('name', 'NOMBRE'))
      with col_font:
          font_options = [font_name.replace('.ttf', '') for font_name in os.listdir('fonts') if font_name.endswith('.ttf')]
          selected_font = st.selectbox("Selecciona la fuente", font_options, index=font_options.index(st.session_state.get('selected_font', font_options[0])))

      # Inputs de color
      col3, col4 = st.columns(2)
      with col3:
          text_border_color1 = st.color_picker("Elige el color del borde del texto en Sticker 1", value=st.session_state.get('text_border_color1', '#000000'))
      with col4:
          text_color1 = st.color_picker("Elige el color del texto en Sticker 1", value=st.session_state.get('text_color1', '#FFFFFF'))

      # Inputs adicionales para personalizar stickers
      col5, col6 = st.columns(2)
      with col5:
          font_size_input1 = st.slider("Tamaño de la tipografía (px)", min_value=20, max_value=400, value=st.session_state.get('font_size_input1', 200))
      with col6:
          border_thickness1 = st.slider("Espesor del borde del texto (px)", min_value=0, max_value=20, value=st.session_state.get('border_thickness1', 10))

      col7, col8 = st.columns(2)
      with col7:
          text_margin_top1 = st.slider("Margen superior del texto (mm)", min_value=0, max_value=200, value=st.session_state.get('text_margin_top1', 30))
      with col8:
          text_alignment1 = st.selectbox("Alineación del texto", ["Izquierda", "Derecha", "Centrado"], index=["Izquierda", "Derecha", "Centrado"].index(st.session_state.get('text_alignment1', 'Izquierda')))

  with col2:
      if image_url:
          # Cargar imagen de fondo
          # background = Image.open(image_url).convert("RGBA")
          response = requests.get(image_url)
          background = Image.open(io.BytesIO(response.content)).convert("RGBA")
          
          width, height = 1400 , 1000  # Dimensiones en píxeles para 7x5 cm a 100 ppi
          sticker1 = Image.new("RGBA", (width, height), (255, 255, 255, 0))
          draw = ImageDraw.Draw(sticker1)

          # Redimensionar la imagen de fondo con efecto tipo cover
          bg_width, bg_height = background.size
          aspect_ratio = max(width / bg_width, height / bg_height)
          new_size = (int(bg_width * aspect_ratio), int(bg_height * aspect_ratio))
          background = background.resize(new_size)
          background = background.crop(((background.width - width) // 2, (background.height - height) // 2, (background.width + width) // 2, (background.height + height) // 2))

          # Dibujar el cuadro blanco con esquinas redondeadas en la parte inferior
          margin_side = 60  # 2 mm a 100 ppi
          margin_bottom = 60  # 2 mm a 100 ppi
          rounded_rect_height = 240  # 1.2 cm a 100 ppi
          draw.rounded_rectangle(
              [(margin_side, height - rounded_rect_height - margin_bottom), (width - margin_side, height - margin_bottom)],
              radius=25,  # Esquinas redondeadas
              fill="white"
          )

          # Añadir el texto en Sticker 1 con borde y alineación
          font_path = os.path.join("fonts", f"{selected_font}.ttf")  # Ruta al archivo de fuente
          font = ImageFont.truetype(font_path, font_size_input1)
          text_width, text_height = draw.textbbox((0, 0), name, font=font)[2:]
          margin_top_px1 = int(text_margin_top1 * 10)  # Convertir mm a px

          if text_alignment1 == "Centrado":
              text_x1 = (width - text_width) / 2
          elif text_alignment1 == "Izquierda":
              text_x1 = margin_side
          else:  # Derecha
              text_x1 = width - text_width - margin_side

          # Dibujar el borde del texto en Sticker 1
          for x_offset in range(-border_thickness1, border_thickness1 + 1):
              for y_offset in range(-border_thickness1, border_thickness1 + 1):
                  if x_offset != 0 or y_offset != 0:
                      draw.text(
                          (text_x1 + x_offset, margin_top_px1 + y_offset),
                          name,
                          font=font,
                          fill=text_border_color1
                      )

          # Dibujar el texto principal en Sticker 1
          draw.text(
              (text_x1, margin_top_px1),
              name,
              font=font,
              fill=text_color1
          )

          # Añadir la imagen de fondo al sticker
          sticker1 = Image.alpha_composite(background, sticker1)

          # Mostrar el sticker generado
          st.image(sticker1, caption="Sticker 1 (7x5 cm)", use_container_width=True)

  # Sección para el segundo sticker
  col3, col4 = st.columns(2)

  with col3:
      st.header("Configuración de Sticker 2")
      
      icon_url = st.text_input("Pegar URL de icono", value=st.session_state.get('icon_url', ''))

      # Input para cargar la imagen del segundo sticker
      # uploaded_icon = st.file_uploader("Subir imagen del icono para el segundo sticker", type=["png", "jpg", "jpeg"], key="icon")

      # Inputs de color
      col_color1, col_color2, col_color3 = st.columns(3)
      with col_color1:
          bg_color = st.color_picker("Elige el color de fondo para el segundo sticker", value=st.session_state.get('bg_color', '#DC0707'))
      with col_color2:
          text_color2 = st.color_picker("Elige el color del texto en Sticker 2", value=st.session_state.get('text_color2', '#fff'))
      with col_color3:
          text_border_color2 = st.color_picker("Elige el color del borde del texto en Sticker 2", value=st.session_state.get('text_border_color2', '#A20303'))

      # Inputs adicionales para personalizar el texto del segundo sticker
      col_slider1, col_slider2, col_slider3 = st.columns(3)
      with col_slider1:
          font_size_input2 = st.slider("Tamaño de la tipografía (px)", min_value=10, max_value=200, value=st.session_state.get('font_size_input2', 140))
      with col_slider2:
          border_thickness2 = st.slider("Espesor del borde del texto (px)", min_value=0, max_value=20, value=st.session_state.get('border_thickness2', 6))
      with col_slider3:
          text_margin_top2 = st.slider("Margen superior del texto (mm)", min_value=0, max_value=40, value=st.session_state.get('text_margin_top2', 4))

      text_alignment2 = st.selectbox("Alineación del texto en Sticker 2", ["Izquierda", "Derecha", "Centrado"], index=["Izquierda", "Derecha", "Centrado"].index(st.session_state.get('text_alignment2', 'Izquierda')))
  with col4:
      # Crear el segundo sticker
      width2, height2 = 1050, 200  # Dimensiones en píxeles para 5x1 cm a 100 ppi
      sticker2 = Image.new("RGBA", (width2, height2), bg_color)
      draw2 = ImageDraw.Draw(sticker2)

      # Añadir el texto en Sticker 2 con borde y alineación
      font_path = os.path.join("fonts", f"{selected_font}.ttf")  # Ruta al archivo de fuente
      font = ImageFont.truetype(font_path, font_size_input2)
      
      text_width2, text_height2 = draw2.textbbox((0, 0), name, font=font)[2:]
      margin_top_px2 = int(text_margin_top2 * 10)  # Convertir mm a px

      if text_alignment2 == "Centrado":
          text_x2 = (width2 - text_width2) / 2
      elif text_alignment2 == "Izquierda":
          text_x2 = 40  # 1 mm de margen
      else:  # Derecha
          text_x2 = width2 - text_width2 - 10

      # Dibujar el borde del texto en Sticker 2
      for x_offset in range(-border_thickness2, border_thickness2 + 1):
          for y_offset in range(-border_thickness2, border_thickness2 + 1):
              if x_offset != 0 or y_offset != 0:
                  draw2.text(
                      (text_x2 + x_offset, margin_top_px2 + y_offset),
                      name,
                      font=font,
                      fill=text_border_color2
                  )

      # Dibujar el texto principal en Sticker 2
      draw2.text(
          (text_x2, margin_top_px2),
          name,
          font=font,
          fill=text_color2
      )

      # Añadir el icono si se cargó uno
        
      if icon_url:
          response = requests.get(icon_url)
          icon = Image.open(io.BytesIO(response.content)).convert("RGBA")
          # icon = Image.open(uploaded_icon).convert("RGBA")
          icon_height = 180  # 8 mm a 100 ppi
          icon_width = int(icon.width * (icon_height / icon.height))
          icon = icon.resize((icon_width, icon_height))
          sticker2.paste(icon, (width2 - icon_width - 40, (height2 - icon_height) // 2), icon)

      # Mostrar el sticker generado
      st.image(sticker2, caption="Sticker 2 (5x1 cm)", use_container_width=True)


  # Botón para guardar la configuración en la base de datos
  if st.button("Guardar configuración"):
      c.execute('''
          INSERT INTO stickers (document_name, name, font, text_border_color1, text_color1, font_size_input1, border_thickness1, text_margin_top1, text_alignment1, image_url, bg_color, text_color2, text_border_color2, font_size_input2, border_thickness2, text_margin_top2, text_alignment2, icon_url)
          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      ''', (document_name, name, selected_font, text_border_color1, text_color1, font_size_input1, border_thickness1, text_margin_top1, text_alignment1, image_url, bg_color, text_color2, text_border_color2, font_size_input2, border_thickness2, text_margin_top2, text_alignment2, icon_url))
      conn.commit()
      st.success("Configuración guardada con éxito")


  # Botón para descargar el PDF
  if st.button("GENERAR PDF"):
      pdf = FPDF('P', 'mm', 'A4')
      pdf.add_page()

      # Guardar Sticker 1 en un archivo temporal
      sticker1_path = "/tmp/sticker1.png"
      sticker1.save(sticker1_path)

      separacion_sticker = 0.3 # 0.2 mm de separación entre stickers
      
      # Añadir Sticker 1 al PDF
      for i in range(2):  # 2 filas
          for j in range(3):  # 3 columnas
              x = j * (70 + separacion_sticker)  # 70 mm de ancho + 0.1 mm de separación
              y = i * (50 + separacion_sticker)  # 50 mm de alto + 0.1 mm de separación
              pdf.image(sticker1_path, x=x, y=y, w=70, h=50)

      # Guardar Sticker 2 en un archivo temporal
      sticker2_path = "/tmp/sticker2.png"
      sticker2.save(sticker2_path)

      # Añadir Sticker 2 al PDF
      for i in range(19):  # 20 filas
          for j in range(4):  # 4 columnas
              x = j * (52.5 + separacion_sticker)  # 50 mm de ancho + 0.1 mm de separación
              y = 100 + i * (10 + separacion_sticker)  # 10 cm de margen superior + 10 mm de alto + 0.1 mm de separación
              pdf.image(sticker2_path, x=x, y=y, w=52.5, h=10)

      # Guardar el PDF en un buffer
      pdf_buffer = io.BytesIO()
      pdf_output = pdf.output(dest='S').encode('latin1')
      pdf_buffer.write(pdf_output)
      pdf_buffer.seek(0)

      # Descargar el PDF
      st.download_button(
          label="Descargar PDF",
          data=pdf_buffer,
          file_name="stickers.pdf",
          mime="application/pdf"
      )
      
      

  # Listado de stickers guardados
  st.title("Stickers guardados")

  # Mostrar los stickers en filas de 6 columnas
  for i in range(0, len(stickers), 12):
      cols = st.columns(12)
      for idx, sticker in enumerate(stickers[i:i+6]):
          with cols[idx]:
              if sticker[2]:  # Si hay una URL de imagen
                  response = requests.get(sticker[2])
                  image = Image.open(io.BytesIO(response.content)).resize((100, 70))
                  st.image(image)
              if st.button(sticker[1], key=sticker[0]):
                  sticker_data = c.execute('SELECT * FROM stickers WHERE id = ?', (sticker[0],)).fetchone()
                  st.session_state['document_name'] = sticker_data[1]
                  st.session_state['name'] = sticker_data[2]
                  st.session_state['selected_font'] = sticker_data[3]
                  st.session_state['text_border_color1'] = sticker_data[4]
                  st.session_state['text_color1'] = sticker_data[5]
                  st.session_state['font_size_input1'] = sticker_data[6]
                  st.session_state['border_thickness1'] = sticker_data[7]
                  st.session_state['text_margin_top1'] = sticker_data[8]
                  st.session_state['text_alignment1'] = sticker_data[9]
                  st.session_state['image_url'] = sticker_data[10]
                  st.session_state['bg_color'] = sticker_data[11]
                  st.session_state['text_color2'] = sticker_data[12]
                  st.session_state['text_border_color2'] = sticker_data[13]
                  st.session_state['font_size_input2'] = sticker_data[14]
                  st.session_state['border_thickness2'] = sticker_data[15]
                  st.session_state['text_margin_top2'] = sticker_data[16]
                  st.session_state['text_alignment2'] = sticker_data[17]
                  st.session_state['icon_url'] = sticker_data[18]


elif section == "Otra Sección":
    st.title("Otra Sección")
    st.write("Contenido de otra sección")